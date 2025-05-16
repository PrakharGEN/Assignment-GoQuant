import logging
import tkinter as tk
from tkinter import ttk
import math

logger = logging.getLogger(__name__)

class MetricWidget(ttk.Frame):
    def __init__(self, parent, title, initial_value="0.00", unit=""):
        super().__init__(parent)
        self.setup_ui(title, initial_value, unit)
        
    def setup_ui(self, title, initial_value, unit):
        # Title
        title_label = ttk.Label(self, text=title, font=('Helvetica', 10))
        title_label.pack(anchor=tk.W)
        
        # Value
        self.value_label = ttk.Label(self, text=f"{initial_value} {unit}", font=('Helvetica', 14, 'bold'))
        self.value_label.pack(anchor=tk.W)
        
        # Add border and padding
        self.configure(padding=10, relief="solid", borderwidth=1)
        
    def update_value(self, value, precision=4):
        """Update the displayed value"""
        if isinstance(value, (int, float)):
            formatted_value = f"{value:.{precision}f}"
        else:
            formatted_value = str(value)
        self.value_label.configure(text=formatted_value)

class OutputPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = ttk.Label(self, text="Real-time Metrics", font=('Helvetica', 16, 'bold'))
        title.pack(pady=(0, 10))
        
        # Grid frame for metrics
        grid = ttk.Frame(self)
        grid.pack(fill=tk.BOTH, expand=True)
        
        # Create metric widgets
        self.slippage_widget = MetricWidget(grid, "Expected Slippage", "0.00", "%")
        self.fees_widget = MetricWidget(grid, "Expected Fees", "0.00", "USD")
        self.impact_widget = MetricWidget(grid, "Market Impact", "0.00", "%")
        self.net_cost_widget = MetricWidget(grid, "Net Cost", "0.00", "USD")
        self.maker_taker_widget = MetricWidget(grid, "Maker Probability", "0.00", "%")
        self.latency_widget = MetricWidget(grid, "Internal Latency", "0.00", "ms")
        
        # Grid layout
        self.slippage_widget.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.fees_widget.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        self.impact_widget.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.net_cost_widget.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        self.maker_taker_widget.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.latency_widget.grid(row=2, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        # Configure grid weights
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
    
    def update_metrics(self, params):
        """Update all metrics based on new parameters"""
        try:
            # Extract parameters
            quantity = params['quantity']
            volatility = params['volatility']
            fee_tier = params['fee_tier']
            
            # Calculate fee percentage based on VIP tier
            fee_map = {
                "VIP 0 (0.10%)": 0.0010,
                "VIP 1 (0.08%)": 0.0008,
                "VIP 2 (0.07%)": 0.0007,
                "VIP 3 (0.06%)": 0.0006,
                "VIP 4 (0.05%)": 0.0005,
                "VIP 5 (0.04%)": 0.0004
            }
            fee_rate = fee_map.get(fee_tier, 0.0010)
            
            # Calculate expected slippage (increases with quantity and volatility)
            slippage = (quantity / 10000) * volatility * 0.01
            
            # Calculate fees
            fees = quantity * fee_rate
            
            # Calculate market impact (using simplified Almgren-Chriss)
            impact = math.sqrt(quantity) * volatility * 0.0002
            
            # Calculate net cost
            net_cost = fees + (quantity * (slippage + impact))
            
            # Calculate maker probability (decreases with size and volatility)
            maker_prob = max(0, min(100, 80 - (quantity/1000) - (volatility * 0.2)))
            
            # Calculate internal latency (increases with complexity)
            latency = 1 + (quantity / 1000) * 0.1
            
            # Update UI
            self.slippage_widget.update_value(slippage * 100)  # Convert to percentage
            self.fees_widget.update_value(fees)
            self.impact_widget.update_value(impact * 100)  # Convert to percentage
            self.net_cost_widget.update_value(net_cost)
            self.maker_taker_widget.update_value(maker_prob)
            self.latency_widget.update_value(latency)
            
            logger.info("Metrics updated successfully")
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}") 