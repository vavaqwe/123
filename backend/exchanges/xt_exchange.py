import aiohttp
import time
import hmac
import hashlib
from typing import Dict, List, Optional
from .base_exchange import BaseExchange
import logging

logger = logging.getLogger(__name__)

class XTExchange(BaseExchange):
    """XT.com Exchange Integration"""
    
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.base_url = "https://sapi.xt.com"
    
    def _generate_signature(self, params: Dict) -> str:
        param_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        return hmac.new(self.api_secret.encode(), param_str.encode(), hashlib.sha256).hexdigest()
    
    async def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json', 'X-XT-APIKEY': self.api_key}
        
        if signed:
            timestamp = str(int(time.time() * 1000))
            params = params or {}
            params['timestamp'] = timestamp
            params['signature'] = self._generate_signature(params)
        
        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url, params=params, headers=headers) as resp:
                    return await resp.json()
            elif method == 'POST':
                async with session.post(url, json=params, headers=headers) as resp:
                    return await resp.json()
    
    async def get_balance(self) -> Dict[str, float]:
        try:
            result = await self._request('GET', '/v4/balances', signed=True)
            return result.get('result', {})
        except Exception as e:
            logger.error(f"XT get_balance error: {e}")
            return {}
    
    async def get_orderbook(self, symbol: str) -> Dict:
        try:
            result = await self._request('GET', '/v4/public/depth', {'symbol': symbol, 'limit': 20})
            return result.get('result', {'bids': [], 'asks': []})
        except Exception as e:
            logger.error(f"XT get_orderbook error: {e}")
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
            
            result = await self._request('POST', '/v4/order', params, signed=True)
            return result
        except Exception as e:
            logger.error(f"XT create_order error: {e}")
            return {'error': str(e)}
    
    async def get_ticker(self, symbol: str) -> Dict:
        try:
            result = await self._request('GET', '/v4/public/ticker/24h', {'symbol': symbol})
            return result.get('result', {})
        except Exception as e:
            logger.error(f"XT get_ticker error: {e}")
            return {}
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
            result = await self._request('GET', '/v4/orders', params, signed=True)
            return result.get('result', [])
        except Exception as e:
            logger.error(f"XT get_open_orders error: {e}")
            return []
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            params = {'orderId': order_id}
            result = await self._request('DELETE', '/v4/order', params, signed=True)
            return result.get('rc') == 0
        except Exception as e:
            logger.error(f"XT cancel_order error: {e}")
            return False