from typing import Dict
import logging

logger = logging.getLogger(__name__)

class FeeCalculator:
    def __init__(self):
        # OKX fee tiers (maker/taker fees)
        self.fee_tiers = {
            "VIP 0 (0.10%)": (0.0008, 0.0010),
            "VIP 1 (0.08%)": (0.0006, 0.0008),
            "VIP 2 (0.07%)": (0.0005, 0.0007),
            "VIP 3 (0.06%)": (0.0004, 0.0006),
            "VIP 4 (0.05%)": (0.0003, 0.0005),
            "VIP 5 (0.04%)": (0.0002, 0.0004)
        }
    
    def calculate_fees(self,
                      order_value: float,
                      fee_tier: str,
                      maker_probability: float) -> Dict[str, float]:
        """
        Calculate expected trading fees
        
        Args:
            order_value: Total value of the order in USD
            fee_tier: Selected fee tier (VIP level)
            maker_probability: Probability of order being maker
        
        Returns:
            Dictionary containing fee calculations
        """
        try:
            # Get maker/taker fees for the tier
            maker_fee, taker_fee = self.fee_tiers.get(
                fee_tier,
                self.fee_tiers["VIP 0 (0.10%)"]  # Default to VIP 0
            )
            
            # Calculate expected fee based on maker probability
            taker_probability = 1 - maker_probability
            expected_fee_rate = (
                maker_fee * maker_probability +
                taker_fee * taker_probability
            )
            
            # Calculate fees
            maker_fee_amount = order_value * maker_fee
            taker_fee_amount = order_value * taker_fee
            expected_fee_amount = order_value * expected_fee_rate
            
            # Convert to basis points
            expected_fee_bps = expected_fee_rate * 10000
            
            return {
                'maker_fee': maker_fee_amount,
                'taker_fee': taker_fee_amount,
                'expected_fee': expected_fee_amount,
                'expected_fee_bps': expected_fee_bps,
                'maker_fee_rate': maker_fee,
                'taker_fee_rate': taker_fee
            }
            
        except Exception as e:
            logger.error(f"Error calculating fees: {str(e)}")
            return {
                'maker_fee': 0.0,
                'taker_fee': 0.0,
                'expected_fee': 0.0,
                'expected_fee_bps': 0.0,
                'maker_fee_rate': 0.0,
                'taker_fee_rate': 0.0
            }
    
    def get_fee_tiers(self) -> Dict[str, tuple]:
        """Return available fee tiers"""
        return self.fee_tiers.copy()
    
    def get_tier_rates(self, tier: str) -> tuple:
        """Get maker/taker rates for a specific tier"""
        return self.fee_tiers.get(
            tier,
            self.fee_tiers["VIP 0 (0.10%)"]
        ) 