#!/usr/bin/env python3
"""
Crypto Trading Bot - Main Entry Point
Monitors blockchains (ETH, BSC, Solana) and executes trades on multiple exchanges
"""

import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from bot.blockchain_monitor import BlockchainMonitor
from bot.trading_engine import TradingEngine
from bot.telegram_notifier import TelegramNotifier
from bot.dex_client import DEXClient

# Exchanges
from exchanges.bybit_exchange import BybitExchange
from exchanges.bingx_exchange import BingXExchange
from exchanges.gate_exchange import GateExchange
from exchanges.okx_exchange import OKXExchange
from exchanges.xt_exchange import XTExchange

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/crypto_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self):
        # MongoDB connection
        mongo_url = os.environ['MONGO_URL']
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[os.environ.get('DB_NAME', 'crypto_trading_bot')]
        
        # Initialize components
        self.telegram = TelegramNotifier()
        self.dex_client = DEXClient()
        self.blockchain_monitor = BlockchainMonitor(
            self.db,
            dex_client=self.dex_client,
            telegram=self.telegram
        )
        
        # Get bot configuration
        self.config = {
            'min_spread': 2.0,
            'max_spread': 3.0,
            'min_liquidity': 10000,
            'min_volume_24h': 50000,
            'trade_amount': 100,
            'auto_trading': os.getenv('ALLOW_LIVE_TRADING', 'False').lower() == 'true',
            'active_blockchains': ['eth', 'bsc', 'solana'],
            'active_exchanges': []
        }
        
        # Initialize trading engine
        self.trading_engine = TradingEngine(self.db, self.config)
        
        # Initialize exchanges
        self.initialize_exchanges()
    
    def initialize_exchanges(self):
        """Initialize exchange connections based on available API keys"""
        
        # Bybit
        if os.getenv('BYBIT_API_KEY') and os.getenv('BYBIT_API_SECRET'):
            try:
                bybit = BybitExchange(
                    os.getenv('BYBIT_API_KEY'),
                    os.getenv('BYBIT_API_SECRET'),
                    testnet=False
                )
                self.trading_engine.add_exchange('bybit', bybit)
                self.config['active_exchanges'].append('bybit')
                logger.info("Bybit exchange initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Bybit: {e}")
        
        # BingX
        if os.getenv('BINGX_API_KEY') and os.getenv('BINGX_API_SECRET'):
            try:
                bingx = BingXExchange(
                    os.getenv('BINGX_API_KEY'),
                    os.getenv('BINGX_API_SECRET')
                )
                self.trading_engine.add_exchange('bingx', bingx)
                self.config['active_exchanges'].append('bingx')
                logger.info("BingX exchange initialized")
            except Exception as e:
                logger.error(f"Failed to initialize BingX: {e}")
        
        # Gate.io
        if os.getenv('GATE_API_KEY') and os.getenv('GATE_API_SECRET'):
            try:
                gate = GateExchange(
                    os.getenv('GATE_API_KEY'),
                    os.getenv('GATE_API_SECRET')
                )
                self.trading_engine.add_exchange('gate', gate)
                self.config['active_exchanges'].append('gate')
                logger.info("Gate.io exchange initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gate.io: {e}")
        
        # OKX
        if os.getenv('OKX_API_KEY') and os.getenv('OKX_API_SECRET'):
            try:
                okx = OKXExchange(
                    os.getenv('OKX_API_KEY'),
                    os.getenv('OKX_API_SECRET'),
                    os.getenv('OKX_PASSPHRASE', '')
                )
                self.trading_engine.add_exchange('okx', okx)
                self.config['active_exchanges'].append('okx')
                logger.info("OKX exchange initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OKX: {e}")
        
        # XT.com
        if os.getenv('XT_API_KEY') and os.getenv('XT_API_SECRET'):
            try:
                xt = XTExchange(
                    os.getenv('XT_API_KEY'),
                    os.getenv('XT_API_SECRET')
                )
                self.trading_engine.add_exchange('xt', xt)
                self.config['active_exchanges'].append('xt')
                logger.info("XT.com exchange initialized")
            except Exception as e:
                logger.error(f"Failed to initialize XT.com: {e}")
        
        if not self.config['active_exchanges']:
            logger.warning("No exchanges initialized! Please configure API keys in .env")
    
    async def start(self):
        """Start the trading bot"""
        logger.info("=" * 60)
        logger.info("🚀 Crypto Trading Bot Starting...")
        logger.info("=" * 60)
        logger.info(f"Active Blockchains: {', '.join(self.config['active_blockchains'])}")
        logger.info(f"Active Exchanges: {', '.join(self.config['active_exchanges'])}")
        logger.info(f"Auto Trading: {'ENABLED ✅' if self.config['auto_trading'] else 'DISABLED ⚠️'}")
        logger.info(f"Target Spread: {self.config['min_spread']}% - {self.config['max_spread']}%")
        logger.info("=" * 60)
        
        # Send startup notification
        await self.telegram.send_message(
            "🤖 <b>Crypto Trading Bot Started</b>\\n\\n"
            f"Mode: {'<b>LIVE TRADING</b>' if self.config['auto_trading'] else '<b>SIMULATION</b>'}\\n"
            f"Exchanges: {len(self.config['active_exchanges'])}\\n"
            f"Blockchains: {len(self.config['active_blockchains'])}"
        )
        
        try:
            # Start all components
            await asyncio.gather(
                self.blockchain_monitor.start(),
                self.trading_engine.start(),
                self.heartbeat(),
                return_exceptions=True
            )
        except Exception as e:
            logger.error(f"Bot error: {e}")
            await self.telegram.send_message(f"❌ <b>Bot Error:</b> {str(e)}")
        finally:
            await self.stop()
    
    async def heartbeat(self):
        """Send periodic status updates"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                # Get stats
                stats = {
                    'total_signals': await self.db.signals.count_documents({}),
                    'total_trades': await self.db.trades.count_documents({}),
                    'open_trades': await self.db.trades.count_documents({'status': 'open'})
                }
                
                await self.telegram.send_status_update(stats)
                
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping trading bot...")
        
        await self.blockchain_monitor.stop()
        await self.trading_engine.stop()
        
        self.client.close()
        
        await self.telegram.send_message("🛑 <b>Crypto Trading Bot Stopped</b>")
        logger.info("Bot stopped successfully")

async def main():
    """Main entry point"""
    bot = TradingBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await bot.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown complete")
