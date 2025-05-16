import json
import logging
import asyncio
import websockets
from datetime import datetime
from collections import deque
from typing import Dict, List, Optional
from src.utils.vpn_handler import VPNHandler

logger = logging.getLogger(__name__)

class OrderBookEntry:
    def __init__(self, price: float, size: float):
        self.price = price
        self.size = size

class OrderBook:
    def __init__(self, max_depth: int = 100):
        self.asks: List[OrderBookEntry] = []
        self.bids: List[OrderBookEntry] = []
        self.max_depth = max_depth
        self.last_update: Optional[datetime] = None
        self.callbacks = []
    
    def add_callback(self, callback):
        """Add callback for orderbook updates"""
        self.callbacks.append(callback)
    
    def update(self, asks: List[List[float]], bids: List[List[float]]):
        """Update orderbook with new data"""
        self.asks = [OrderBookEntry(price=ask[0], size=ask[1]) 
                    for ask in asks[:self.max_depth]]
        self.bids = [OrderBookEntry(price=bid[0], size=bid[1]) 
                    for bid in bids[:self.max_depth]]
        self.last_update = datetime.now()
        
        # Notify callbacks
        for callback in self.callbacks:
            callback(self)
    
    def get_mid_price(self) -> float:
        """Calculate mid price"""
        if not self.asks or not self.bids:
            return 0.0
        return (self.asks[0].price + self.bids[0].price) / 2
    
    def get_spread(self) -> float:
        """Calculate spread"""
        if not self.asks or not self.bids:
            return 0.0
        return self.asks[0].price - self.bids[0].price
    
    def get_depth(self, side: str, price_level: float) -> float:
        """Calculate cumulative depth up to price level"""
        entries = self.asks if side.lower() == 'ask' else self.bids
        cum_size = 0.0
        
        for entry in entries:
            if (side.lower() == 'ask' and entry.price <= price_level) or \
               (side.lower() == 'bid' and entry.price >= price_level):
                cum_size += entry.size
        
        return cum_size

class WebSocketClient:
    def __init__(self, url: str = "wss://ws.okx.com:8443/ws/v5/public"):
        self.url = url
        self.orderbook = OrderBook()
        self.connected = False
        self.processing_times = deque(maxlen=100)
        self.vpn_handler = VPNHandler()
        
    async def connect(self):
        """Establish WebSocket connection"""
        # Check VPN connection first
        vpn_status = self.vpn_handler.check_connection()
        if not vpn_status["status"]:
            logger.error(f"VPN check failed: {vpn_status['message']}")
            return False
            
        try:
            self.ws = await websockets.connect(self.url)
            self.connected = True
            logger.info(f"Connected to WebSocket at {self.url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {str(e)}")
            return False
    
    async def subscribe(self):
        """Subscribe to orderbook updates"""
        try:
            subscribe_msg = {
                "op": "subscribe",
                "args": [{
                    "channel": "books",
                    "instId": "BTC-USDT-SWAP"
                }]
            }
            await self.ws.send(json.dumps(subscribe_msg))
            logger.info("Subscribed to OKX orderbook updates")
        except Exception as e:
            logger.error(f"Failed to subscribe: {str(e)}")
    
    async def process_message(self, message: str) -> Dict:
        """Process incoming WebSocket message"""
        try:
            start_time = datetime.now()
            
            data = json.loads(message)
            if 'data' in data:
                orderbook_data = data['data'][0]
                if 'asks' in orderbook_data and 'bids' in orderbook_data:
                    # Convert string prices and sizes to float
                    asks = [[float(price), float(size)] for price, size, *_ in orderbook_data['asks']]
                    bids = [[float(price), float(size)] for price, size, *_ in orderbook_data['bids']]
                    
                    self.orderbook.update(asks, bids)
                    
                    # Calculate processing time
                    processing_time = (datetime.now() - start_time).total_seconds() * 1000
                    self.processing_times.append(processing_time)
                    
                    return {
                        'mid_price': self.orderbook.get_mid_price(),
                        'spread': self.orderbook.get_spread(),
                        'processing_time': processing_time,
                        'timestamp': data.get('ts', datetime.now().timestamp() * 1000)
                    }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {}
    
    def get_average_latency(self) -> float:
        """Calculate average processing latency"""
        if not self.processing_times:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)
    
    async def close(self):
        """Close WebSocket connection"""
        if self.connected:
            await self.ws.close()
            self.connected = False
            logger.info("WebSocket connection closed")
    
    async def run(self):
        """Main run loop"""
        while True:
            try:
                if not self.connected:
                    if not await self.connect():
                        await asyncio.sleep(5)  # Wait before retrying
                        continue
                    await self.subscribe()
                
                async for message in self.ws:
                    await self.process_message(message)
                    
            except websockets.ConnectionClosed:
                logger.warning("WebSocket connection closed. Attempting to reconnect...")
                self.connected = False
            except Exception as e:
                logger.error(f"Error in run loop: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
            finally:
                if self.connected:
                    await self.close() 