from typing import Optional, Union, Literal
import numpy as np

class SlippageModel:
    """
    A comprehensive slippage model that simulates trading execution costs.
    Supports fixed, percentage-based, and volume-based slippage calculations.
    """
    
    def __init__(
        self,
        model_type: Literal["fixed", "percentage", "volume"] = "percentage",
        fixed_slippage: float = 0.0,
        percentage_slippage: float = 0.001,  # 0.1% default
        volume_impact_factor: float = 0.1,
        min_slippage: float = 0.0,
        max_slippage: Optional[float] = None
    ):
        """
        Initialize the slippage model.
        
        Args:
            model_type: Type of slippage model to use
            fixed_slippage: Fixed amount to add/subtract from price
            percentage_slippage: Percentage of price to use as slippage
            volume_impact_factor: Factor for volume-based slippage
            min_slippage: Minimum slippage amount
            max_slippage: Maximum slippage amount (optional)
        """
        self.model_type = model_type
        self.fixed_slippage = fixed_slippage
        self.percentage_slippage = percentage_slippage
        self.volume_impact_factor = volume_impact_factor
        self.min_slippage = min_slippage
        self.max_slippage = max_slippage

    def calculate_slippage(
        self,
        price: float,
        volume: float,
        is_buy: bool,
        market_volume: Optional[float] = None
    ) -> float:
        """
        Calculate slippage based on the configured model type.
        
        Args:
            price: Current asset price
            volume: Trade volume
            is_buy: True if buying, False if selling
            market_volume: Optional market volume for volume-based calculations
            
        Returns:
            float: Price after slippage application
        """
        slippage = 0.0
        
        if self.model_type == "fixed":
            slippage = self._calculate_fixed_slippage(is_buy)
        elif self.model_type == "percentage":
            slippage = self._calculate_percentage_slippage(price, is_buy)
        elif self.model_type == "volume":
            slippage = self._calculate_volume_slippage(price, volume, market_volume, is_buy)
            
        # Apply min/max bounds if configured
        if self.max_slippage is not None:
            slippage = min(slippage, self.max_slippage)
        slippage = max(slippage, self.min_slippage)
        
        return price + (slippage if is_buy else -slippage)

    def _calculate_fixed_slippage(self, is_buy: bool) -> float:
        """Calculate fixed slippage amount."""
        return self.fixed_slippage

    def _calculate_percentage_slippage(self, price: float, is_buy: bool) -> float:
        """Calculate percentage-based slippage."""
        return price * self.percentage_slippage

    def _calculate_volume_slippage(
        self,
        price: float,
        volume: float,
        market_volume: Optional[float],
        is_buy: bool
    ) -> float:
        """
        Calculate volume-based slippage.
        Uses square root formula if market_volume is available,
        otherwise falls back to linear impact.
        """
        if market_volume:
            # Square root formula for price impact
            volume_ratio = volume / market_volume
            slippage = price * self.volume_impact_factor * np.sqrt(volume_ratio)
        else:
            # Linear impact when market volume unknown
            slippage = price * self.volume_impact_factor * (volume / 1000)  # Arbitrary scaling
            
        return slippage 
