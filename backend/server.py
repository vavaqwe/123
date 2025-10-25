from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# WebSocket manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Models
class Exchange(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # bybit, binance, gate, okx, xt
    api_key: str
    api_secret: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExchangeCreate(BaseModel):
    name: str
    api_key: str
    api_secret: str
    is_active: bool = True

class Signal(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    blockchain: str  # eth, bsc, solana
    token_address: str
    token_symbol: Optional[str] = None
    event_type: str  # pool_creation, large_swap, liquidity_add
    price: float
    liquidity: float
    volume_24h: Optional[float] = None
    spread: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"  # pending, notified, executed, skipped

class Trade(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_id: str
    exchange: str
    symbol: str
    side: str  # buy, sell
    entry_price: float
    exit_price: Optional[float] = None
    amount: float
    profit: Optional[float] = None
    spread: float
    status: str = "open"  # open, closed, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None

class BotConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    min_spread: float = 2.0  # 2%
    max_spread: float = 3.0  # 3%
    min_liquidity: float = 10000.0
    min_volume_24h: float = 50000.0
    trade_amount: float = 100.0
    auto_trading: bool = False
    active_blockchains: List[str] = ["eth", "bsc", "solana"]
    active_exchanges: List[str] = ["bybit", "binance", "gate", "okx", "xt"]
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Stats(BaseModel):
    total_signals: int = 0
    total_trades: int = 0
    open_trades: int = 0
    total_profit: float = 0.0
    today_profit: float = 0.0
    success_rate: float = 0.0

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Crypto Trading Bot API", "status": "running"}

# Exchange Management
@api_router.post("/exchanges", response_model=Exchange)
async def create_exchange(exchange: ExchangeCreate):
    exchange_obj = Exchange(**exchange.model_dump())
    doc = exchange_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.exchanges.insert_one(doc)
    return exchange_obj

@api_router.get("/exchanges", response_model=List[Exchange])
async def get_exchanges():
    exchanges = await db.exchanges.find({}, {"_id": 0}).to_list(1000)
    for ex in exchanges:
        if isinstance(ex['created_at'], str):
            ex['created_at'] = datetime.fromisoformat(ex['created_at'])
    return exchanges

@api_router.delete("/exchanges/{exchange_id}")
async def delete_exchange(exchange_id: str):
    result = await db.exchanges.delete_one({"id": exchange_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return {"message": "Exchange deleted"}

# Signal Management
@api_router.get("/signals", response_model=List[Signal])
async def get_signals(limit: int = 100):
    signals = await db.signals.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    for sig in signals:
        if isinstance(sig['timestamp'], str):
            sig['timestamp'] = datetime.fromisoformat(sig['timestamp'])
    return signals

@api_router.post("/signals", response_model=Signal)
async def create_signal(signal: Signal):
    doc = signal.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.signals.insert_one(doc)
    
    # Broadcast to WebSocket clients
    await manager.broadcast({"type": "new_signal", "data": doc})
    return signal

# Trade Management
@api_router.get("/trades", response_model=List[Trade])
async def get_trades(limit: int = 100):
    trades = await db.trades.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    for trade in trades:
        if isinstance(trade['created_at'], str):
            trade['created_at'] = datetime.fromisoformat(trade['created_at'])
        if trade.get('closed_at') and isinstance(trade['closed_at'], str):
            trade['closed_at'] = datetime.fromisoformat(trade['closed_at'])
    return trades

@api_router.post("/trades", response_model=Trade)
async def create_trade(trade: Trade):
    doc = trade.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('closed_at'):
        doc['closed_at'] = doc['closed_at'].isoformat()
    await db.trades.insert_one(doc)
    
    # Broadcast to WebSocket clients
    await manager.broadcast({"type": "new_trade", "data": doc})
    return trade

# Bot Configuration
@api_router.get("/config", response_model=BotConfig)
async def get_config():
    config = await db.bot_config.find_one({}, {"_id": 0})
    if not config:
        # Create default config
        default_config = BotConfig()
        doc = default_config.model_dump()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.bot_config.insert_one(doc)
        return default_config
    
    if isinstance(config['updated_at'], str):
        config['updated_at'] = datetime.fromisoformat(config['updated_at'])
    return BotConfig(**config)

@api_router.put("/config", response_model=BotConfig)
async def update_config(config: BotConfig):
    doc = config.model_dump()
    doc['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.bot_config.delete_many({})
    await db.bot_config.insert_one(doc)
    
    doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
    return BotConfig(**doc)

# Statistics
@api_router.get("/stats", response_model=Stats)
async def get_stats():
    total_signals = await db.signals.count_documents({})
    total_trades = await db.trades.count_documents({})
    open_trades = await db.trades.count_documents({"status": "open"})
    
    # Calculate profits
    closed_trades = await db.trades.find({"status": "closed"}, {"_id": 0}).to_list(1000)
    total_profit = sum(trade.get('profit', 0) for trade in closed_trades)
    
    # Today's profit
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_trades = [t for t in closed_trades if isinstance(t.get('closed_at'), str) and 
                    datetime.fromisoformat(t['closed_at']) >= today_start]
    today_profit = sum(trade.get('profit', 0) for trade in today_trades)
    
    # Success rate
    success_rate = 0.0
    if len(closed_trades) > 0:
        profitable_trades = [t for t in closed_trades if t.get('profit', 0) > 0]
        success_rate = (len(profitable_trades) / len(closed_trades)) * 100
    
    return Stats(
        total_signals=total_signals,
        total_trades=total_trades,
        open_trades=open_trades,
        total_profit=total_profit,
        today_profit=today_profit,
        success_rate=success_rate
    )

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()