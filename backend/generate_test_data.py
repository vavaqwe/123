#!/usr/bin/env python3
"""
Generate test data for the crypto trading bot demo
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import random
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def generate_test_data():
    """Generate test signals and trades for demo purposes"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'crypto_trading_bot')]
    
    print("🎲 Generating test data...")
    
    # Clear existing test data
    await db.signals.delete_many({})
    await db.trades.delete_many({})
    
    # Generate test signals
    blockchains = ['eth', 'bsc', 'solana']
    event_types = ['pool_creation', 'large_swap', 'liquidity_add']
    statuses = ['pending', 'notified', 'executed', 'skipped']
    
    signals = []
    for i in range(20):
        timestamp = datetime.now(timezone.utc) - timedelta(hours=random.randint(0, 48))
        signal = {
            'id': f"signal_{i}_{int(timestamp.timestamp())}",
            'blockchain': random.choice(blockchains),
            'token_address': f"0x{''.join([random.choice('0123456789abcdef') for _ in range(40)])}",
            'token_symbol': f"TOKEN{i}",
            'event_type': random.choice(event_types),
            'price': round(random.uniform(0.000001, 100), 6),
            'liquidity': round(random.uniform(5000, 500000), 2),
            'volume_24h': round(random.uniform(10000, 1000000), 2),
            'spread': round(random.uniform(1.5, 4.0), 2),
            'timestamp': timestamp.isoformat(),
            'status': random.choice(statuses)
        }
        signals.append(signal)
    
    await db.signals.insert_many(signals)
    print(f"✅ Created {len(signals)} test signals")
    
    # Generate test trades
    exchanges = ['bybit', 'binance', 'gate', 'okx', 'xt']
    symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'MATIC/USDT']
    
    trades = []
    for i in range(15):
        created_at = datetime.now(timezone.utc) - timedelta(hours=random.randint(0, 72))
        is_closed = random.choice([True, True, False])  # 66% closed
        
        entry_price = round(random.uniform(10, 50000), 6)
        spread = round(random.uniform(2.0, 3.0), 2)
        exit_price = entry_price * (1 + spread / 100) if is_closed else None
        amount = round(random.uniform(0.01, 1.0), 6)
        
        trade = {
            'id': f"trade_{i}_{int(created_at.timestamp())}",
            'signal_id': f"signal_{random.randint(0, 19)}",
            'exchange': random.choice(exchanges),
            'symbol': random.choice(symbols),
            'side': 'buy',
            'entry_price': entry_price,
            'exit_price': exit_price,
            'amount': amount,
            'spread': spread,
            'status': 'closed' if is_closed else 'open',
            'created_at': created_at.isoformat()
        }
        
        if is_closed:
            closed_at = created_at + timedelta(hours=random.randint(1, 24))
            trade['closed_at'] = closed_at.isoformat()
            trade['profit'] = round((exit_price - entry_price) * amount, 2)
        
        trades.append(trade)
    
    await db.trades.insert_many(trades)
    print(f"✅ Created {len(trades)} test trades")
    
    # Create default bot config
    config = {
        'id': 'default_config',
        'min_spread': 2.0,
        'max_spread': 3.0,
        'min_liquidity': 10000.0,
        'min_volume_24h': 50000.0,
        'trade_amount': 100.0,
        'auto_trading': False,
        'active_blockchains': ['eth', 'bsc', 'solana'],
        'active_exchanges': ['bybit', 'binance', 'gate', 'okx', 'xt'],
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.bot_config.delete_many({})
    await db.bot_config.insert_one(config)
    print("✅ Created default bot config")
    
    client.close()
    print("\n🎉 Test data generation complete!")
    print("📊 You can now view the data in the web dashboard")

if __name__ == "__main__":
    asyncio.run(generate_test_data())
