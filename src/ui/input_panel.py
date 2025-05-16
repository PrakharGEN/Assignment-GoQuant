import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)

class InputPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.on_parameters_updated = None
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = ttk.Label(self, text="Trade Parameters", font=('Helvetica', 16, 'bold'))
        title.pack(pady=(0, 10))
        
        # Form frame
        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.X, padx=10)
        
        # Asset selection
        ttk.Label(form_frame, text="Asset:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.asset_combo = ttk.Combobox(form_frame, values=["BTC-USDT-SWAP"], state="readonly")
        self.asset_combo.current(0)
        self.asset_combo.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Order type (disabled as only Market is supported)
        ttk.Label(form_frame, text="Order Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.order_type = ttk.Combobox(form_frame, values=["Market"], state="disabled")
        self.order_type.current(0)
        self.order_type.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Quantity input
        ttk.Label(form_frame, text="Quantity (USD):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar(value="100")
        self.quantity_spin = ttk.Spinbox(
            form_frame,
            from_=1,
            to=1000,
            textvariable=self.quantity_var,
            increment=1
        )
        self.quantity_spin.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Volatility input
        ttk.Label(form_frame, text="Volatility (%):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.volatility_var = tk.StringVar(value="50")
        self.volatility_spin = ttk.Spinbox(
            form_frame,
            from_=0,
            to=200,
            textvariable=self.volatility_var,
            increment=1
        )
        self.volatility_spin.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Fee tier selection
        ttk.Label(form_frame, text="Fee Tier:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.fee_tier_combo = ttk.Combobox(form_frame, values=[
            "VIP 0 (0.10%)",
            "VIP 1 (0.08%)",
            "VIP 2 (0.07%)",
            "VIP 3 (0.06%)",
            "VIP 4 (0.05%)",
            "VIP 5 (0.04%)"
        ], state="readonly")
        self.fee_tier_combo.current(0)
        self.fee_tier_combo.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # Configure grid columns
        form_frame.columnconfigure(1, weight=1)
        
        # Add some spacing
        ttk.Frame(self).pack(pady=10)
        
        # Simulate button
        self.simulate_btn = ttk.Button(
            self,
            text="Simulate Trade",
            command=self.on_simulate,
            style="Accent.TButton"
        )
        self.simulate_btn.pack(fill=tk.X, padx=10)
        
        # Configure button style
        style = ttk.Style()
        style.configure("Accent.TButton", background="#2ecc71")
        
        # Bind events
        self.quantity_var.trace_add("write", lambda *args: self.on_parameter_change())
        self.volatility_var.trace_add("write", lambda *args: self.on_parameter_change())
        self.fee_tier_combo.bind("<<ComboboxSelected>>", lambda e: self.on_parameter_change())
    
    def get_parameters(self):
        """Collect all input parameters"""
        try:
            quantity = float(self.quantity_var.get())
            volatility = float(self.volatility_var.get()) / 100  # Convert to decimal
        except ValueError:
            quantity = 100
            volatility = 0.5
            
        return {
            'asset': self.asset_combo.get(),
            'order_type': self.order_type.get(),
            'quantity': quantity,
            'volatility': volatility,
            'fee_tier': self.fee_tier_combo.get()
        }
    
    def on_simulate(self):
        """Handle simulate button click"""
        if self.on_parameters_updated:
            params = self.get_parameters()
            logger.info(f"Simulating trade with parameters: {params}")
            self.on_parameters_updated(params)
    
    def on_parameter_change(self):
        """Handle parameter changes"""
        self.on_simulate()  # Auto-update on any parameter change 