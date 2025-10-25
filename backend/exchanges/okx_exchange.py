import aiohttp
import time
import hmac
import hashlib
import base64
from typing import Dict, List, Optional
from .base_exchange import BaseExchange
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class OKXExchange(BaseExchange):
    """OKX Exchange Integration"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str = ""):
        super().__init__(api_key, api_secret)
        self.passphrase = passphrase
        self.base_url = "https://www.okx.com"
    
    def _generate_signature(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        message = timestamp + method + request_path + body
        mac = hmac.new(self.api_secret.encode(), message.encode(), hashlib.sha256)
        return base64.b64encode(mac.digest()).decode()
    
    async def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if signed:
            timestamp = datetime.utcnow().isoformat()[:-3] + 'Z'
            body = json.dumps(params) if params and method == 'POST' else ''
            request_path = endpoint
            
            signature = self._generate_signature(timestamp, method, request_path, body)
            headers['OK-ACCESS-KEY'] = self.api_key
            headers['OK-ACCESS-SIGN'] = signature
            headers['OK-ACCESS-TIMESTAMP'] = timestamp
            headers['OK-ACCESS-PASSPHRASE'] = self.passphrase
        
        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url, params=params, headers=headers) as resp:
                    return await resp.json()
            elif method == 'POST':
                async with session.post(url, json=params, headers=headers) as resp:
                    return await resp.json()
    
    async def get_balance(self) -> Dict[str, float]:
        try:
            result = await self._request('GET', '/api/v5/account/balance', signed=True)
            return result.get('data', [])
        except Exception as e:
            logger.error(f"OKX get_balance error: {e}")
            return {}
    
    async def get_orderbook(self, symbol: str) -> Dict:
        try:
            result = await self._request('GET', '/api/v5/market/books', {'instId': symbol, 'sz': '20'})
            data = result.get('data', [{}])[0]
            return {'bids': data.get('bids', []), 'asks': data.get('asks', [])}
        except Exception as e:
            logger.error(f"OKX get_orderbook error: {e}")
            return {'bids': [], 'asks': []}
    
    async def create_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict:
        try:
            params = {
                'instId': symbol,
                'tdMode': 'cash',
                'side': side,
                'ordType': 'market' if price is None else 'limit',
                'sz': str(amount)
            }
            if price:
                params['px'] = str(price)
            
            result = await self._request('POST', '/api/v5/trade/order', params, signed=True)
            return result
        except Exception as e:
            logger.error(f"OKX create_order error: {e}")
            return {'error': str(e)}
    
    async def get_ticker(self, symbol: str) -> Dict:
        try:
            result = await self._request('GET', '/api/v5/market/ticker', {'instId': symbol})
            return result.get('data', [{}])[0]
        except Exception as e:
            logger.error(f"OKX get_ticker error: {e}")
            return {}
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        try:
            params = {}
            if symbol:
                params['instId'] = symbol
            result = await self._request('GET', '/api/v5/trade/orders-pending', params, signed=True)
            return result.get('data', [])
        except Exception as e:
            logger.error(f"OKX get_open_orders error: {e}")
            return []
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        try:
            params = {'instId': symbol, 'ordId': order_id}
            result = await self._request('POST', '/api/v5/trade/cancel-order', params, signed=True)
            return result.get('code') == '0'
        except Exception as e:
            logger.error(f"OKX cancel_order error: {e}")
            return False