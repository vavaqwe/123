import asyncio
import logging
from typing import Dict, List
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from web3.exceptions import BlockNotFound
import aiohttp

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

class BlockchainMonitor:
    """Monitor blockchain events from ETH, BSC, and Solana"""
    
    def __init__(self, db, dex_client=None, telegram=None):
        self.db = db
        self.dex_client = dex_client
        self.telegram = telegram
        self.running = False
        
        # Web3 connections
        self.eth_rpc = os.getenv('ETH_RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/demo')
        self.bsc_rpc = os.getenv('BSC_RPC_URL', 'https://bsc-dataseed.binance.org/')
        self.sol_rpc = os.getenv('SOL_RPC_URL', 'https://api.mainnet-beta.solana.com')
        
        # Initialize Web3
        try:
            self.w3_eth = Web3(Web3.HTTPProvider(self.eth_rpc))
            self.w3_bsc = Web3(Web3.HTTPProvider(self.bsc_rpc))
            logger.info(f"Web3 ETH connected: {self.w3_eth.is_connected()}")
            logger.info(f"Web3 BSC connected: {self.w3_bsc.is_connected()}")
        except Exception as e:
            logger.error(f"Error initializing Web3: {e}")
            self.w3_eth = None
            self.w3_bsc = None
        
        # Uniswap V2 Factory address (for new pair detection)
        self.uniswap_factory = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
        self.pancakeswap_factory = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
        
        # Last processed block numbers
        self.last_eth_block = None
        self.last_bsc_block = None
        
        # DEXScreener monitoring mode
        self.use_dexscreener = True  # Простіший режим через DEXScreener API
        
    async def start(self):
        """Start monitoring blockchains"""
        self.running = True
        logger.info("Starting blockchain monitor...")
        logger.info(f"Monitoring mode: {'DEXScreener API' if self.use_dexscreener else 'Web3 Events'}")
        
        # Start monitoring tasks
        if self.use_dexscreener:
            # Простіший підхід - моніторинг через DEXScreener
            tasks = [
                self.monitor_dexscreener_trending(),
                self.monitor_dexscreener_new_pairs()
            ]
        else:
            # Складніший підхід - прямий моніторинг блокчейну
            tasks = [
                self.monitor_ethereum(),
                self.monitor_bsc(),
                self.monitor_solana()
            ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Stopping blockchain monitor...")
    
    async def monitor_dexscreener_trending(self):
        """Monitor trending tokens from DEXScreener"""
        logger.info("🔥 Monitoring DEXScreener trending tokens...")
        
        while self.running:
            try:
                async with aiohttp.ClientSession() as session:
                    # Отримуємо топ токени по різних мережах
                    chains = ['ethereum', 'bsc', 'solana']
                    
                    for chain in chains:
                        try:
                            url = f"https://api.dexscreener.com/latest/dex/search?q={chain}"
                            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    pairs = data.get('pairs', [])[:5]  # Топ 5 пар
                                    
                                    for pair in pairs:
                                        await self.process_dexscreener_pair(pair, chain)
                            
                            await asyncio.sleep(2)  # Затримка між запитами
                            
                        except Exception as e:
                            logger.error(f"Error fetching trending for {chain}: {e}")
                
                await asyncio.sleep(60)  # Перевірка кожну хвилину
                
            except Exception as e:
                logger.error(f"Error in DEXScreener trending monitor: {e}")
                await asyncio.sleep(30)
    
    async def monitor_dexscreener_new_pairs(self):
        """Monitor new pairs from DEXScreener"""
        logger.info("🆕 Monitoring DEXScreener new pairs...")
        
        while self.running:
            try:
                async with aiohttp.ClientSession() as session:
                    # DEXScreener нові пари endpoint
                    url = "https://api.dexscreener.com/latest/dex/pairs/ethereum,bsc,solana"
                    
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            pairs = data.get('pairs', [])
                            
                            # Фільтруємо нові пари (створені менше 24 годин тому)
                            for pair in pairs[:10]:  # Обробляємо топ 10
                                pair_created_at = pair.get('pairCreatedAt', 0)
                                if pair_created_at > 0:
                                    created_timestamp = datetime.fromtimestamp(pair_created_at / 1000, tz=timezone.utc)
                                    age_hours = (datetime.now(timezone.utc) - created_timestamp).total_seconds() / 3600
                                    
                                    if age_hours < 24:  # Пара створена менше 24 годин тому
                                        await self.process_dexscreener_pair(pair, pair.get('chainId', 'unknown'))
                
                await asyncio.sleep(120)  # Перевірка кожні 2 хвилини
                
            except Exception as e:
                logger.error(f"Error in DEXScreener new pairs monitor: {e}")
                await asyncio.sleep(30)
    
    async def process_dexscreener_pair(self, pair: Dict, chain: str):
        """Process pair data from DEXScreener and create signal"""
        try:
            # Витягуємо дані
            token_address = pair.get('baseToken', {}).get('address', '')
            token_symbol = pair.get('baseToken', {}).get('symbol', 'UNKNOWN')
            price_usd = float(pair.get('priceUsd', 0) or 0)
            liquidity_usd = float(pair.get('liquidity', {}).get('usd', 0) or 0)
            volume_24h = float(pair.get('volume', {}).get('h24', 0) or 0)
            price_change_24h = float(pair.get('priceChange', {}).get('h24', 0) or 0)
            
            # Фільтр за мінімальними вимогами
            if liquidity_usd < 5000 or volume_24h < 10000:
                return
            
            # Перевіряємо чи сигнал вже існує
            existing = await self.db.signals.find_one({'token_address': token_address})
            if existing:
                return  # Вже є такий сигнал
            
            # Визначаємо тип події
            event_type = 'pool_creation' if pair.get('pairCreatedAt', 0) > 0 else 'trending'
            
            # Обчислюємо спред (приблизно з volume/liquidity ratio)
            spread = 0
            if liquidity_usd > 0:
                spread = min((volume_24h / liquidity_usd) * 0.1, 5.0)  # Максимум 5%
            
            # Створюємо сигнал
            signal = await self.create_signal(
                blockchain=chain,
                token_address=token_address,
                token_symbol=token_symbol,
                event_type=event_type,
                price=price_usd,
                liquidity=liquidity_usd,
                volume_24h=volume_24h,
                spread=spread
            )
            
            if signal and self.telegram:
                await self.telegram.send_signal_notification(signal)
                logger.info(f"📢 Signal created and sent: {token_symbol} on {chain}")
            
        except Exception as e:
            logger.error(f"Error processing DEXScreener pair: {e}")
    
    async def monitor_ethereum(self):
        """Monitor Ethereum blockchain via Web3"""
        logger.info("⛓️ Monitoring Ethereum via Web3...")
        
        if not self.w3_eth or not self.w3_eth.is_connected():
            logger.error("Ethereum Web3 not connected")
            return
        
        while self.running:
            try:
                latest_block = self.w3_eth.eth.block_number
                
                if self.last_eth_block is None:
                    self.last_eth_block = latest_block - 1
                
                # Process new blocks
                for block_num in range(self.last_eth_block + 1, latest_block + 1):
                    try:
                        block = self.w3_eth.eth.get_block(block_num, full_transactions=True)
                        await self.process_block_transactions(block, 'ethereum')
                    except BlockNotFound:
                        continue
                
                self.last_eth_block = latest_block
                await asyncio.sleep(12)  # Ethereum block time ~12s
                
            except Exception as e:
                logger.error(f"Error monitoring Ethereum: {e}")
                await asyncio.sleep(5)
    
    async def monitor_bsc(self):
        """Monitor BSC blockchain via Web3"""
        logger.info("⛓️ Monitoring BSC via Web3...")
        
        if not self.w3_bsc or not self.w3_bsc.is_connected():
            logger.error("BSC Web3 not connected")
            return
        
        while self.running:
            try:
                latest_block = self.w3_bsc.eth.block_number
                
                if self.last_bsc_block is None:
                    self.last_bsc_block = latest_block - 1
                
                for block_num in range(self.last_bsc_block + 1, latest_block + 1):
                    try:
                        block = self.w3_bsc.eth.get_block(block_num, full_transactions=True)
                        await self.process_block_transactions(block, 'bsc')
                    except BlockNotFound:
                        continue
                
                self.last_bsc_block = latest_block
                await asyncio.sleep(3)  # BSC block time ~3s
                
            except Exception as e:
                logger.error(f"Error monitoring BSC: {e}")
                await asyncio.sleep(5)
    
    async def monitor_solana(self):
        """Monitor Solana blockchain"""
        logger.info("⛓️ Monitoring Solana...")
        
        while self.running:
            try:
                # Solana моніторинг через RPC (складніша реалізація)
                # Для початку використовуємо тільки DEXScreener
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error monitoring Solana: {e}")
                await asyncio.sleep(30)
    
    async def process_block_transactions(self, block, chain: str):
        """Process transactions in a block to detect DEX events"""
        try:
            # Тут можна аналізувати транзакції на предмет:
            # - PairCreated events від Uniswap/PancakeSwap factory
            # - Великі Swap події
            # - Додавання ліквідності
            
            # Це потребує декодування event logs
            # Для простоти зараз пропускаємо
            pass
            
        except Exception as e:
            logger.error(f"Error processing block transactions: {e}")
    
    async def create_signal(self, blockchain: str, token_address: str, event_type: str, 
                           price: float, liquidity: float, volume_24h: float = 0):
        """Create a new signal in the database"""
        try:
            signal = {
                'id': str(datetime.now(timezone.utc).timestamp()),
                'blockchain': blockchain,
                'token_address': token_address,
                'event_type': event_type,
                'price': price,
                'liquidity': liquidity,
                'volume_24h': volume_24h,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'pending'
            }
            
            await self.db.signals.insert_one(signal)
            logger.info(f"Created signal: {blockchain} - {token_address}")
            return signal
            
        except Exception as e:
            logger.error(f"Error creating signal: {e}")