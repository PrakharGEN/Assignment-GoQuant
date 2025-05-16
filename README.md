# Crypto Trading Simulator with Performance Monitoring

A high-performance trade simulator that leverages real-time market data to estimate transaction costs and market impact. The system connects to OKX WebSocket endpoints for streaming full L2 orderbook data.

## Features

### 1. Real-Time Market Data
- Live connection to OKX WebSocket API
- Full L2 orderbook data streaming
- Real-time price and spread monitoring
- Market depth visualization

### 2. Trading Simulation
- Market impact calculation using Almgren-Chriss model
- Maker/Taker prediction using machine learning
- Fee calculation based on VIP tiers
- Transaction cost analysis

### 3. Performance Monitoring
- CPU and memory usage tracking
- Network latency monitoring
- Thread management
- System resource optimization

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd crypto-trading-simulator
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Usage

1. Ensure VPN connection for OKX access
2. Run the main application:
```bash
python src/main.py
```

## System Architecture

### Components
1. **WebSocket Client**
   - Real-time market data connection
   - Order book management
   - Data processing pipeline

2. **Market Impact Model**
   - Almgren-Chriss implementation
   - Price impact calculation
   - Volatility adjustment

3. **Maker/Taker Predictor**
   - Machine learning model
   - Feature normalization
   - Probability calculation

4. **Performance Monitor**
   - Resource usage tracking
   - Latency measurement
   - System optimization

## Performance Analysis

### 1. Latency Benchmarking

#### Data Processing Latency
- WebSocket Message Processing: ~0.5ms per message
- Order Book Update: ~0.2ms
- Market Impact Calculation: ~0.3ms
- Total Processing Pipeline: ~1.0ms

#### UI Update Latency
- Market Data Display: 16.67ms (60 FPS)
- Trade Simulation Updates: ~5ms
- Chart Rendering: ~8ms

#### End-to-end Simulation Loop
- Average Loop Time: ~25ms
- 95th Percentile: ~40ms
- 99th Percentile: ~60ms

### 2. Optimization Techniques

#### Memory Management
- Fixed-size collections (deque, lists)
- Efficient garbage collection (-0.10 MB/s growth)
- Average Memory Usage: 52.25 MB
- Peak Memory Usage: 62.79 MB

#### Network Communication
- Async WebSocket handling
- Message filtering at source
- Binary message optimization
- Average Bandwidth: 373.5 MB/s

#### Data Structure Selection
- OrderBook: O(1) updates
- Price Levels: Sorted arrays
- Historical Data: Circular buffers
- Memory-mapped files for logging

### 3. Model Implementation

#### Almgren-Chriss Market Impact Model
```python
def calculate_impact(self, quantity, price, volatility, market_depth):
    # Temporary impact: η|v|^γ
    temp_impact = self.temporary_impact * np.sqrt(quantity) * price
    
    # Permanent impact: θv
    perm_impact = self.permanent_impact * quantity * price
    
    # Volatility adjustment
    vol_adjustment = volatility / self.volatility
    temp_impact *= vol_adjustment
    perm_impact *= vol_adjustment
```

#### Maker/Taker Prediction Model
```python
def predict_maker_probability(self, spread, market_depth, volatility, order_size):
    # Feature normalization
    norm_spread = spread / price
    norm_depth = np.log1p(market_depth)
    norm_size = order_size / market_depth
    
    # Probability calculation
    features = np.array([[norm_spread, norm_depth, volatility, norm_size]])
    maker_prob = self.model.predict_proba(features)[0][1]
```

### 4. Benchmarking Results

#### System Performance
- CPU Usage: 10.44% average, 69.30% peak
- Memory: 52.25 MB average, 62.79 MB peak
- Network: 373.5 MB/s average bandwidth
- Thread Count: 17 active threads

#### Model Performance
- Market Impact Calculation: ~0.3ms
- Maker/Taker Prediction: ~0.2ms
- Order Book Updates: ~0.2ms
- Total Model Pipeline: ~0.7ms

### 5. Future Optimizations

1. **Memory Management**
   - Implement memory pooling
   - Add compression for historical data
   - Optimize object allocation

2. **Network Performance**
   - Add message compression
   - Implement connection pooling
   - Optimize heartbeat frequency

3. **Model Efficiency**
   - Add model parameter caching
   - Implement batch prediction
   - Optimize feature calculation

4. **Thread Management**
   - Add thread pool for calculations
   - Optimize thread synchronization
   - Implement work stealing

## Project Structure
```
crypto-trading-simulator/
├── src/
│   ├── data/           # Market data handling
│   ├── models/         # Trading models
│   ├── ui/            # User interface
│   └── utils/         # Utilities
├── docs/
│   └── performance_data/  # Performance reports
├── tests/             # Test cases
└── README.md          # This file
```

## Dependencies
- Python 3.8+
- websockets
- numpy
- scikit-learn
- tkinter
- requests

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License
[MIT License](LICENSE)

## Authors
[Prakhar Mishra]

## Acknowledgments
- OKX for providing market data access
- Almgren-Chriss for market impact model
- Open source community 
