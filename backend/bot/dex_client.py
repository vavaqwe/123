import aiohttp
import logging
from typing import Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

class DEXClient:
    """Client for fetching DEX data from various sources"""
    
    def __init__(self):
        self.dexscreener_url = "https://api.dexscreener.com/latest/dex"
    
    async def get_token_info(self, chain: str, token_address: str) -> Optional[Dict]:
        """Get token information from DEXScreener"""
        try:
            url = f"{self.dexscreener_url}/tokens/{token_address}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get('pairs', [])
                        
                        if pairs:
                            # Return the first pair with highest liquidity
                            pairs_sorted = sorted(pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0)), reverse=True)
                            return pairs_sorted[0] if pairs_sorted else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching token info: {e}")
            return None
    
    async def get_pair_info(self, chain: str, pair_address: str) -> Optional[Dict]:
        """Get pair information from DEXScreener"""
        try:
            url = f"{self.dexscreener_url}/pairs/{chain}/{pair_address}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get('pairs', [])
                        return pairs[0] if pairs else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching pair info: {e}")
            return None
    
    async def search_pairs(self, query: str) -> list:
        """Search for pairs by query"""
        try:
            url = f"{self.dexscreener_url}/search?q={query}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('pairs', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching pairs: {e}")
            return []