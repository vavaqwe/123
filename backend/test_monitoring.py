#!/usr/bin/env python3
"""
Demo: Test DEXScreener monitoring
Показує як працює моніторинг сигналів через DEXScreener API
"""

import asyncio
import aiohttp
import sys
from datetime import datetime

async def test_dexscreener():
    """Test DEXScreener API and show how signals are detected"""
    
    print("=" * 70)
    print("🔍 ТЕСТ DEXSCREENER МОНІТОРИНГУ")
    print("=" * 70)
    print()
    
    print("📡 Підключаємось до DEXScreener API...")
    print()
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Trending tokens
        print("1️⃣  Тест: Trending токени (Ethereum)")
        print("-" * 70)
        
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=ethereum"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pairs = data.get('pairs', [])[:3]  # Топ 3
                    
                    print(f"✅ Знайдено {len(pairs)} пар")
                    print()
                    
                    for i, pair in enumerate(pairs, 1):
                        token_symbol = pair.get('baseToken', {}).get('symbol', 'UNKNOWN')
                        token_address = pair.get('baseToken', {}).get('address', '')[:10]
                        price_usd = float(pair.get('priceUsd', 0) or 0)
                        liquidity = float(pair.get('liquidity', {}).get('usd', 0) or 0)
                        volume_24h = float(pair.get('volume', {}).get('h24', 0) or 0)
                        price_change = float(pair.get('priceChange', {}).get('h24', 0) or 0)
                        
                        print(f"   {i}. {token_symbol}")
                        print(f"      Address: {token_address}...")
                        print(f"      Price: ${price_usd:.6f}")
                        print(f"      Liquidity: ${liquidity:,.0f}")
                        print(f"      Volume 24h: ${volume_24h:,.0f}")
                        print(f"      Change 24h: {price_change:+.2f}%")
                        
                        # Перевіряємо чи пройде фільтр
                        if liquidity >= 5000 and volume_24h >= 10000:
                            print(f"      ✅ ПРОЙШОВ ФІЛЬТР - створюємо сигнал!")
                        else:
                            print(f"      ❌ Не пройшов фільтр (ліквідність або об'єм занизькі)")
                        print()
                else:
                    print(f"❌ Помилка: HTTP {resp.status}")
        except Exception as e:
            print(f"❌ Помилка: {e}")
        
        print()
        print("=" * 70)
        print()
        
        # Test 2: Specific token search
        print("2️⃣  Тест: Пошук конкретного токену (WETH)")
        print("-" * 70)
        
        try:
            url = "https://api.dexscreener.com/latest/dex/tokens/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pairs = data.get('pairs', [])[:2]  # Топ 2 пари
                    
                    print(f"✅ Знайдено {len(pairs)} пар для WETH")
                    print()
                    
                    for i, pair in enumerate(pairs, 1):
                        dex_name = pair.get('dexId', 'unknown')
                        pair_address = pair.get('pairAddress', '')[:10]
                        liquidity = float(pair.get('liquidity', {}).get('usd', 0) or 0)
                        
                        print(f"   {i}. DEX: {dex_name}")
                        print(f"      Pair: {pair_address}...")
                        print(f"      Liquidity: ${liquidity:,.0f}")
                        print()
                else:
                    print(f"❌ Помилка: HTTP {resp.status}")
        except Exception as e:
            print(f"❌ Помилка: {e}")
        
        print()
        print("=" * 70)
        print()
        
        # Summary
        print("📊 ВИСНОВОК:")
        print("-" * 70)
        print("""
Моніторинг працює так:

1. 🔄 Кожну 1 хвилину - перевіряємо trending токени
2. 🔄 Кожні 2 хвилини - перевіряємо нові пари
3. 🔍 Фільтруємо по ліквідності (≥$5,000) та об'єму (≥$10,000)
4. 💾 Створюємо сигнали в MongoDB
5. 📱 Відправляємо Telegram сповіщення

Переваги DEXScreener:
✅ Безкоштовний
✅ Не потребує RPC ключів
✅ Покриває всі мережі (ETH, BSC, Solana)
✅ Готові агреговані дані
        """)
        
        print()
        print("🚀 Щоб запустити реальний моніторинг:")
        print("   cd /app/backend")
        print("   python bot_main.py")
        print()
        print("=" * 70)

if __name__ == "__main__":
    try:
        asyncio.run(test_dexscreener())
    except KeyboardInterrupt:
        print("\n\n👋 Тест зупинено")
        sys.exit(0)
