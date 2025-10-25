import aiohttp
import time
import hmac
import hashlib
from typing import Dict, List, Optional
from .base_exchange import BaseExchange
import logging

logger = logging.getLogger(__name__)

class BingXExchange(BaseExchange):
    """BingX Exchange Integration"""
    
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.base_url = "https://open-api.bingx.com"
    
    def _generate_signature(self, params: str) -> str:
        return hmac.new(self.api_secret.encode(), params.encode(), hashlib.sha256).hexdigest()
    
    async def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        url = f"{self.base_url}{endpoint}"
        headers = {"X-BX-APIKEY": self.api_key}
        
        if signed:
            timestamp = str(int(time.time() * 1000))
            params = params or {}
            params['timestamp'] = timestamp
            param_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            params['signature'] = self._generate_signature(param_str)
        
        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url, params=params, headers=headers) as resp:
                    return await resp.json()
            elif method == 'POST':
                async with session.post(url, json=params, headers=headers) as resp:
                    return await resp.json()
    
    async def get_balance(self) -> Dict[str, float]:
        try:
            result = await self._request('GET', '/openApi/spot/v1/account/balance', signed=True)
            return result.get('data', {})
        except Exception as e:
            logger.error(f"BingX get_balance error: {e}")
            return {}
    
    async def get_orderbook(self, symbol: str) -> Dict:
        try:
            result = await self._request('GET', '/openApi/spot/v1/market/depth', {'symbol': symbol, 'limit': 20})
            return result.get('data', {'bids': [], 'asks': []})
        except Exception as e:
            logger.error(f"BingX get_orderbook error: {e}")
            return {'bids': [], 'asks': []}
    
    async def create_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict:
        try:
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': 'MARKET' if price is None else 'LIMIT',
                'quantity': amount
            }
            if price:
                params['price'] = price
            
            result = await self._request('POST', '/openApi/spot/v1/trade/order', params, signed=True)
            return result
        except Exception as e:
            logger.error(f"BingX create_order error: {e}")
            return {'error': str(e)}
    
    async def get_ticker(self, symbol: str) -> Dict:
        try:
            result = await self._request('GET', '/openApi/spot/v1/ticker/24hr', {'symbol': symbol})
            return result.get('data', {})
        except Exception as e:
            logger.error(f"BingX get_ticker error: {e}")
            return {}
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
            result = await self._request('GET', '/openApi/spot/v1/trade/openOrders', params, signed=True)
            return result.get('data', {}).get('orders', [])
        except Exception as e:
            logger.error(f"BingX get_open_orders error: {e}")
            return []
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            params = {'symbol': symbol, 'orderId': order_id}
            result = await self._request('POST', '/openApi/spot/v1/trade/cancel', params, signed=True)
            return result.get('code') == 0
        except Exception as e:
            logger.error(f"BingX cancel_order error: {e}")
            return False