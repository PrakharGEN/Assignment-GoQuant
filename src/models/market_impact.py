import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AlmgrenChrissModel:
    def __init__(self):
        # Model parameters (can be calibrated based on historical data)
        self.permanent_impact = 2.5e-6  # Permanent price impact parameter
        self.temporary_impact = 2.5e-6  # Temporary price impact parameter
        self.volatility = 0.3          # Asset volatility (annualized)
        
    def calculate_impact(self, 
                        quantity: float,
                        price: float,
                        volatility: Optional[float] = None,
                        market_depth: Optional[float] = None) -> Dict[str, float]:
        """
        Calculate market impact using Almgren-Chriss model
        
        Args:
            quantity: Order size in base currency
            price: Current asset price
            volatility: Optional override for volatility
            market_depth: Optional market depth at current price level
        
        Returns:
            Dictionary containing temporary and permanent impact
        """
        try:
            # Use provided volatility if available
            vol = volatility if volatility is not None else self.volatility
            
            # Calculate order value
            order_value = quantity * price
            
            # Temporary impact calculation
            # η|v|^γ where η is temporary_impact, v is volume, γ typically = 0.5
            temp_impact = self.temporary_impact * np.sqrt(quantity) * price
            
            # Permanent impact calculation
            # θv where θ is permanent_impact, v is volume
            perm_impact = self.permanent_impact * quantity * price
            
            # Adjust impacts based on volatility
            vol_adjustment = vol / self.volatility
            temp_impact *= vol_adjustment
            perm_impact *= vol_adjustment
            
            # Adjust for market depth if provided
            if market_depth is not None and market_depth > 0:
                depth_adjustment = np.sqrt(quantity / market_depth)
                temp_impact *= depth_adjustment
                perm_impact *= depth_adjustment
            
            total_impact = temp_impact + perm_impact
            impact_bps = (total_impact / order_value) * 10000  # Convert to basis points
            
            return {
                'temporary_impact': temp_impact,
                'permanent_impact': perm_impact,
                'total_impact': total_impact,
                'impact_bps': impact_bps
            }
            
        except Exception as e:
            logger.error(f"Error calculating market impact: {str(e)}")
            return {
                'temporary_impact': 0.0,
                'permanent_impact': 0.0,
                'total_impact': 0.0,
                'impact_bps': 0.0
            }
    
    def update_parameters(self,
                         permanent_impact: Optional[float] = None,
                         temporary_impact: Optional[float] = None,
                         volatility: Optional[float] = None):
        """Update model parameters"""
        if permanent_impact is not None:
            self.permanent_impact = permanent_impact
        if temporary_impact is not None:
            self.temporary_impact = temporary_impact
        if volatility is not None:
            self.volatility = volatility
        
        logger.info("Market impact model parameters updated") 