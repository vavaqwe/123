import aiohttp
import time
import hmac
import hashlib
from typing import Dict, List, Optional
from .base_exchange import BaseExchange
import logging

logger = logging.getLogger(__name__)

class GateExchange(BaseExchange):
    """Gate.io Exchange Integration"""
    
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.base_url = "https://api.gateio.ws/api/v4"
    
    def _generate_signature(self, method: str, url: str, query_string: str, payload: str, timestamp: str) -> str:
        message = f"{method}\n{url}\n{query_string}\n{hashlib.sha512(payload.encode()).hexdigest()}\n{timestamp}"
        return hmac.new(self.api_secret.encode(), message.encode(), hashlib.sha512).hexdigest()
    
    async def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        url = f"{self.base_url}{endpoint}"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        if signed:
            timestamp = str(int(time.time()))
            query_string = ''
            payload = ''
            if params:
                if method == 'GET':
                    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
                else:
                    payload = str(params)
            
            signature = self._generate_signature(method, endpoint, query_string, payload, timestamp)
            headers['KEY'] = self.api_key
            headers['Timestamp'] = timestamp
            headers['SIGN'] = signature
        
        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url, params=params, headers=headers) as resp:
                    return await resp.json()
            elif method == 'POST':
                async with session.post(url, json=params, headers=headers) as resp:
                    return await resp.json()
    
    async def get_balance(self) -> Dict[str, float]:
        try:
            result = await self._request('GET', '/spot/accounts', signed=True)
            return {item['currency']: float(item['available']) for item in result}
        except Exception as e:
            logger.error(f"Gate get_balance error: {e}")
            return {}
    
    async def get_orderbook(self, symbol: str) -> Dict:
        try:
            result = await self._request('GET', f'/spot/order_book', {'currency_pair': symbol, 'limit': 20})
            return result
        except Exception as e:
            logger.error(f"Gate get_orderbook error: {e}")
            return {'bids': [], 'asks': []}
    
    async def create_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict:
        try:
            params = {
                'currency_pair': symbol,
                'side': side,
                'amount': str(amount),
                'type': 'market' if price is None else 'limit'
            }
            if price:
                params['price'] = str(price)
            
            result = await self._request('POST', '/spot/orders', params, signed=True)
            return result
        except Exception as e:
            logger.error(f"Gate create_order error: {e}")
            return {'error': str(e)}
    
    async def get_ticker(self, symbol: str) -> Dict:
        try:
            result = await self._request('GET', f'/spot/tickers', {'currency_pair': symbol})
            return result[0] if result else {}
        except Exception as e:
            logger.error(f"Gate get_ticker error: {e}")
            return {}
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        try:
            params = {'status': 'open'}
            if symbol:
                params['currency_pair'] = symbol
            result = await self._request('GET', '/spot/orders', params, signed=True)
            return result
        except Exception as e:
            logger.error(f"Gate get_open_orders error: {e}")
            return []
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            result = await self._request('DELETE', f'/spot/orders/{order_id}', {'currency_pair': symbol}, signed=True)
            return 'id' in result
        except Exception as e:
            logger.error(f"Gate cancel_order error: {e}")
            return False