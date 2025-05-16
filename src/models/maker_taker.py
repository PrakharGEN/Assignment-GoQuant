import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MakerTakerModel:
    def __init__(self):
        self.model = LogisticRegression(random_state=42)
        self.is_trained = False
        
        # Default feature weights (can be updated with training)
        self.spread_weight = 0.4    # Spread contribution
        self.depth_weight = 0.3     # Market depth contribution
        self.vol_weight = -0.2      # Volatility contribution
        self.size_weight = -0.3     # Order size contribution
    
    def train(self,
              features: np.ndarray,
              labels: np.ndarray):
        """
        Train the maker/taker prediction model
        
        Args:
            features: Array of [spread, market_depth, volatility, order_size]
            labels: Binary array (1 for maker, 0 for taker)
        """
        try:
            self.model.fit(features, labels)
            self.is_trained = True
            logger.info("Maker/Taker model trained successfully")
        except Exception as e:
            logger.error(f"Error training maker/taker model: {str(e)}")
    
    def predict_maker_probability(self,
                                spread: float,
                                market_depth: float,
                                volatility: float,
                                order_size: float,
                                price: float) -> Dict[str, float]:
        """
        Predict probability of order being maker vs taker
        
        Args:
            spread: Current bid-ask spread
            market_depth: Available liquidity at current price
            volatility: Current volatility estimate
            order_size: Size of the order
            price: Current asset price
        
        Returns:
            Dictionary containing maker and taker probabilities
        """
        try:
            # Normalize inputs
            norm_spread = spread / price
            norm_depth = np.log1p(market_depth)
            norm_size = order_size / market_depth if market_depth > 0 else 1.0
            
            # Feature vector
            features = np.array([[norm_spread, norm_depth, volatility, norm_size]])
            
            if self.is_trained:
                # Use trained model
                maker_prob = self.model.predict_proba(features)[0][1]
            else:
                # Use simple linear combination with sigmoid activation
                z = (
                    self.spread_weight * norm_spread +
                    self.depth_weight * norm_depth +
                    self.vol_weight * volatility +
                    self.size_weight * norm_size
                )
                maker_prob = 1 / (1 + np.exp(-z))
            
            taker_prob = 1 - maker_prob
            
            return {
                'maker_probability': maker_prob,
                'taker_probability': taker_prob,
                'predicted_type': 'Maker' if maker_prob > 0.5 else 'Taker',
                'confidence': max(maker_prob, taker_prob)
            }
            
        except Exception as e:
            logger.error(f"Error predicting maker/taker probability: {str(e)}")
            return {
                'maker_probability': 0.5,
                'taker_probability': 0.5,
                'predicted_type': 'Unknown',
                'confidence': 0.0
            }
    
    def update_weights(self,
                      spread_weight: Optional[float] = None,
                      depth_weight: Optional[float] = None,
                      vol_weight: Optional[float] = None,
                      size_weight: Optional[float] = None):
        """Update model weights"""
        if spread_weight is not None:
            self.spread_weight = spread_weight
        if depth_weight is not None:
            self.depth_weight = depth_weight
        if vol_weight is not None:
            self.vol_weight = vol_weight
        if size_weight is not None:
            self.size_weight = size_weight
        
        logger.info("Maker/Taker model weights updated") 