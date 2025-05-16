import logging
import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
from src.ui.input_panel import InputPanel
from src.ui.output_panel import OutputPanel
from src.data.websocket_client import WebSocketClient
from src.utils.vpn_handler import VPNHandler

logger = logging.getLogger(__name__)

class MarketDataPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = ttk.Label(self, text="Market Data", font=('Helvetica', 16, 'bold'))
        title.pack(pady=(0, 10))
        
        # Market data frame
        data_frame = ttk.Frame(self)
        data_frame.pack(fill=tk.X, padx=10)
        
        # Labels for market data
        self.price_label = ttk.Label(data_frame, text="Price: --", font=('Helvetica', 12))
        self.price_label.pack(anchor=tk.W, pady=2)
        
        self.spread_label = ttk.Label(data_frame, text="Spread: --", font=('Helvetica', 12))
        self.spread_label.pack(anchor=tk.W, pady=2)
        
        self.depth_label = ttk.Label(data_frame, text="Market Depth: --", font=('Helvetica', 12))
        self.depth_label.pack(anchor=tk.W, pady=2)
        
        self.latency_label = ttk.Label(data_frame, text="Latency: --", font=('Helvetica', 12))
        self.latency_label.pack(anchor=tk.W, pady=2)
        
        # Connection status
        self.status_label = ttk.Label(data_frame, text="Status: Disconnected", font=('Helvetica', 12))
        self.status_label.pack(anchor=tk.W, pady=2)
    
    def update_market_data(self, orderbook):
        """Update market data display"""
        self.price_label.config(text=f"Price: {orderbook.get_mid_price():.2f} USDT")
        self.spread_label.config(text=f"Spread: {orderbook.get_spread():.4f} USDT")
        self.depth_label.config(text=f"Market Depth: {orderbook.get_depth('bid', orderbook.get_mid_price()):.2f} BTC")
        self.status_label.config(text="Status: Connected")

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Crypto Trading Simulator")
        self.geometry("1200x800")
        
        # Initialize components
        self.setup_ui()
        self.setup_market_data()
        
        logger.info("Main window initialized successfully")
    
    def setup_ui(self):
        # Main container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Market data panel (top)
        self.market_panel = MarketDataPanel(container)
        self.market_panel.pack(fill=tk.X, pady=(0, 20))
        
        # Input panel (left)
        self.input_panel = InputPanel(container)
        self.input_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Output panel (right)
        self.output_panel = OutputPanel(container)
        self.output_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Link panels
        self.input_panel.on_parameters_updated = self.output_panel.update_metrics
    
    def setup_market_data(self):
        """Initialize market data connection"""
        self.ws_client = WebSocketClient()
        self.ws_client.orderbook.add_callback(self.market_panel.update_market_data)
        
        # Start WebSocket connection in background
        asyncio.create_task(self.ws_client.run())
    
    def check_vpn(self):
        """Check VPN connection"""
        vpn_handler = VPNHandler()
        status = vpn_handler.check_connection()
        if not status["status"]:
            messagebox.showwarning(
                "VPN Required",
                "Please connect to VPN to access OKX market data."
            )
            return False
        return True
    
    def update_latency(self, latency_ms):
        """Update latency display"""
        self.market_panel.latency_label.config(text=f"Latency: {latency_ms:.2f} ms") 