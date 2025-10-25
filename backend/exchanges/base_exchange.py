from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class BaseExchange(ABC):
    """Base class for all exchange integrations"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        pass
    
    @abstractmethod
    async def get_orderbook(self, symbol: str) -> Dict:
        """Get orderbook for a symbol"""
        pass
    
    @abstractmethod
    async def create_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict:
        """Create a new order"""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict:
        """Get ticker information"""
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        pass
    
    def calculate_spread(self, orderbook: Dict) -> float:
        """Calculate spread from orderbook"""
        try:
            best_bid = float(orderbook['bids'][0][0]) if orderbook.get('bids') else 0
            best_ask = float(orderbook['asks'][0][0]) if orderbook.get('asks') else 0
            
            if best_bid > 0 and best_ask > 0:
                spread = ((best_ask - best_bid) / best_bid) * 100
                return round(spread, 4)
            return 0
        except Exception as e:
            logger.error(f"Error calculating spread: {e}")
            return 0