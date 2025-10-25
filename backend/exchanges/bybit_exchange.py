import aiohttp
import time
import hmac
import hashlib
import json
from typing import Dict, List, Optional
from .base_exchange import BaseExchange
import logging

logger = logging.getLogger(__name__)

class BybitExchange(BaseExchange):
    """Bybit Exchange Integration"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        super().__init__(api_key, api_secret)
        self.base_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature"""
        param_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        return hmac.new(self.api_secret.encode(), param_str.encode(), hashlib.sha256).hexdigest()
    
    async def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if signed:
            timestamp = str(int(time.time() * 1000))
            params = params or {}
            params['api_key'] = self.api_key
            params['timestamp'] = timestamp
            params['sign'] = self._generate_signature(params)
        
        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url, params=params, headers=headers) as resp:
                    return await resp.json()
            elif method == 'POST':
                async with session.post(url, json=params, headers=headers) as resp:
                    return await resp.json()
    
    async def get_balance(self) -> Dict[str, float]:
        try:
            result = await self._request('GET', '/v5/account/wallet-balance', {'accountType': 'UNIFIED'}, signed=True)
            return result.get('result', {})
        except Exception as e:
            logger.error(f"Bybit get_balance error: {e}")
            return {}
    
    async def get_orderbook(self, symbol: str) -> Dict:
        try:
            result = await self._request('GET', '/v5/market/orderbook', {'category': 'spot', 'symbol': symbol})
            return result.get('result', {})
        except Exception as e:
            logger.error(f"Bybit get_orderbook error: {e}")
            return {'bids': [], 'asks': []}
    
    async def create_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict:
        try:
            params = {
                'category': 'spot',
                'symbol': symbol,
                'side': side.capitalize(),
                'orderType': 'Market' if price is None else 'Limit',
                'qty': str(amount)
            }
            if price:
                params['price'] = str(price)
            
            result = await self._request('POST', '/v5/order/create', params, signed=True)
            return result
        except Exception as e:
            logger.error(f"Bybit create_order error: {e}")
            return {'error': str(e)}
    
    async def get_ticker(self, symbol: str) -> Dict:
        try:
            result = await self._request('GET', '/v5/market/tickers', {'category': 'spot', 'symbol': symbol})
            return result.get('result', {})
        except Exception as e:
            logger.error(f"Bybit get_ticker error: {e}")
            return {}
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        try:
            params = {'category': 'spot'}
            if symbol:
                params['symbol'] = symbol
            result = await self._request('GET', '/v5/order/realtime', params, signed=True)
            return result.get('result', {}).get('list', [])
        except Exception as e:
            logger.error(f"Bybit get_open_orders error: {e}")
            return []
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            params = {'category': 'spot', 'symbol': symbol, 'orderId': order_id}
            result = await self._request('POST', '/v5/order/cancel', params, signed=True)
            return result.get('retCode') == 0
        except Exception as e:
            logger.error(f"Bybit cancel_order error: {e}")
            return False