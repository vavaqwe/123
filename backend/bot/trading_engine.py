import logging
from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class TradingEngine:
    """Core trading engine for executing trades based on signals"""
    
    def __init__(self, db, config: Dict):
        self.db = db
        self.config = config
        self.exchanges = {}
        self.running = False
    
    def add_exchange(self, name: str, exchange_client):
        """Add exchange client to the engine"""
        self.exchanges[name] = exchange_client
        logger.info(f"Added exchange: {name}")
    
    async def start(self):
        """Start the trading engine"""
        self.running = True
        logger.info("Starting trading engine...")
        
        while self.running:
            try:
                # Process pending signals
                await self.process_signals()
                
                # Monitor open trades
                await self.monitor_trades()
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in trading engine: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop the trading engine"""
        self.running = False
        logger.info("Stopping trading engine...")
    
    async def process_signals(self):
        """Process pending signals and decide whether to trade"""
        try:
            # Get pending signals
            signals = await self.db.signals.find({"status": "pending"}, {"_id": 0}).limit(10).to_list(10)
            
            for signal in signals:
                # Check if signal meets trading criteria
                if await self.should_trade(signal):
                    # Execute trade if auto_trading is enabled
                    if self.config.get('auto_trading', False):
                        await self.execute_trade(signal)
                    else:
                        # Just mark as notified
                        await self.db.signals.update_one(
                            {"id": signal['id']},
                            {"$set": {"status": "notified"}}
                        )
                        logger.info(f"Signal notified (auto-trading disabled): {signal['id']}")
                else:
                    # Skip signal
                    await self.db.signals.update_one(
                        {"id": signal['id']},
                        {"$set": {"status": "skipped"}}
                    )
                    
        except Exception as e:
            logger.error(f"Error processing signals: {e}")
    
    async def should_trade(self, signal: Dict) -> bool:
        """Determine if a signal meets trading criteria"""
        try:
            # Check liquidity threshold
            if signal.get('liquidity', 0) < self.config.get('min_liquidity', 10000):
                return False
            
            # Check volume threshold
            if signal.get('volume_24h', 0) < self.config.get('min_volume_24h', 50000):
                return False
            
            # Check if we can find this token on any exchange
            # This is a simplified check - in production, implement proper symbol mapping
            return True
            
        except Exception as e:
            logger.error(f"Error checking trade criteria: {e}")
            return False
    
    async def execute_trade(self, signal: Dict):
        """Execute a trade based on a signal"""
        try:
            # Find best exchange for this trade
            best_exchange = await self.find_best_exchange(signal)
            
            if not best_exchange:
                logger.warning(f"No suitable exchange found for signal {signal['id']}")
                return
            
            exchange_name = best_exchange['name']
            exchange_client = self.exchanges.get(exchange_name)
            
            if not exchange_client:
                logger.error(f"Exchange client not found: {exchange_name}")
                return
            
            # Calculate trade parameters
            symbol = best_exchange.get('symbol', 'BTC/USDT')  # Default symbol
            amount = self.config.get('trade_amount', 100.0)
            
            # Get current price and calculate spread
            orderbook = await exchange_client.get_orderbook(symbol)
            spread = exchange_client.calculate_spread(orderbook)
            
            # Check if spread is within acceptable range (2-3%)
            min_spread = self.config.get('min_spread', 2.0)
            max_spread = self.config.get('max_spread', 3.0)
            
            if spread < min_spread or spread > max_spread:
                logger.info(f"Spread {spread}% outside target range {min_spread}-{max_spread}%")
                return
            
            # Create buy order
            best_ask = float(orderbook['asks'][0][0]) if orderbook.get('asks') else 0
            
            if best_ask > 0:
                # Place limit order
                order = await exchange_client.create_order(
                    symbol=symbol,
                    side='buy',
                    amount=amount / best_ask,
                    price=best_ask
                )
                
                if 'error' not in order:
                    # Create trade record
                    trade = {
                        'id': str(datetime.now(timezone.utc).timestamp()),
                        'signal_id': signal['id'],
                        'exchange': exchange_name,
                        'symbol': symbol,
                        'side': 'buy',
                        'entry_price': best_ask,
                        'amount': amount / best_ask,
                        'spread': spread,
                        'status': 'open',
                        'created_at': datetime.now(timezone.utc).isoformat()
                    }
                    
                    await self.db.trades.insert_one(trade)
                    await self.db.signals.update_one(
                        {"id": signal['id']},
                        {"$set": {"status": "executed"}}
                    )
                    
                    logger.info(f"Trade executed: {symbol} on {exchange_name}")
                else:
                    logger.error(f"Error creating order: {order.get('error')}")
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    async def monitor_trades(self):
        """Monitor open trades and close profitable ones"""
        try:
            # Get open trades
            trades = await self.db.trades.find({"status": "open"}, {"_id": 0}).limit(50).to_list(50)
            
            for trade in trades:
                exchange_client = self.exchanges.get(trade['exchange'])
                if not exchange_client:
                    continue
                
                # Get current orderbook
                orderbook = await exchange_client.get_orderbook(trade['symbol'])
                current_spread = exchange_client.calculate_spread(orderbook)
                
                best_bid = float(orderbook['bids'][0][0]) if orderbook.get('bids') else 0
                entry_price = trade['entry_price']
                
                # Calculate profit percentage
                if best_bid > 0 and entry_price > 0:
                    profit_pct = ((best_bid - entry_price) / entry_price) * 100
                    
                    # Close trade if profit is within target spread range
                    target_profit = self.config.get('min_spread', 2.0)
                    
                    if profit_pct >= target_profit:
                        # Place sell order
                        sell_order = await exchange_client.create_order(
                            symbol=trade['symbol'],
                            side='sell',
                            amount=trade['amount'],
                            price=best_bid
                        )
                        
                        if 'error' not in sell_order:
                            profit = (best_bid - entry_price) * trade['amount']
                            
                            await self.db.trades.update_one(
                                {"id": trade['id']},
                                {"$set": {
                                    "status": "closed",
                                    "exit_price": best_bid,
                                    "profit": profit,
                                    "closed_at": datetime.now(timezone.utc).isoformat()
                                }}
                            )
                            
                            logger.info(f"Trade closed with profit: ${profit:.2f}")
                
        except Exception as e:
            logger.error(f"Error monitoring trades: {e}")
    
    async def find_best_exchange(self, signal: Dict) -> Optional[Dict]:
        """Find the best exchange for trading a signal"""
        # In production, implement logic to find which exchange has this token
        # For now, return a default exchange if available
        
        for exchange_name in self.config.get('active_exchanges', []):
            if exchange_name in self.exchanges:
                return {'name': exchange_name, 'symbol': 'BTC/USDT'}
        
        return None