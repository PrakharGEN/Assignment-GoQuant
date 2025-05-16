import time
import logging
from collections import deque
from typing import Dict, Optional
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        
        # Latency tracking
        self.websocket_latencies = deque(maxlen=window_size)
        self.processing_latencies = deque(maxlen=window_size)
        self.ui_update_latencies = deque(maxlen=window_size)
        
        # Tick tracking
        self.tick_times = deque(maxlen=window_size)
        self.tick_rates = deque(maxlen=window_size)
        
        # Memory tracking
        self.memory_usage = deque(maxlen=window_size)
        
        self.start_time = datetime.now()
    
    def record_websocket_latency(self, latency_ms: float):
        """Record WebSocket message latency"""
        self.websocket_latencies.append(latency_ms)
    
    def record_processing_latency(self, latency_ms: float):
        """Record processing latency"""
        self.processing_latencies.append(latency_ms)
    
    def record_ui_latency(self, latency_ms: float):
        """Record UI update latency"""
        self.ui_update_latencies.append(latency_ms)
    
    def record_tick(self):
        """Record a tick arrival"""
        now = datetime.now()
        self.tick_times.append(now)
        
        # Calculate tick rate if we have enough data
        if len(self.tick_times) > 1:
            time_diff = (self.tick_times[-1] - self.tick_times[-2]).total_seconds()
            if time_diff > 0:
                rate = 1.0 / time_diff
                self.tick_rates.append(rate)
    
    def record_memory(self, usage_mb: float):
        """Record memory usage"""
        self.memory_usage.append(usage_mb)
    
    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        try:
            # Calculate latency statistics
            ws_latency = np.mean(self.websocket_latencies) if self.websocket_latencies else 0
            proc_latency = np.mean(self.processing_latencies) if self.processing_latencies else 0
            ui_latency = np.mean(self.ui_update_latencies) if self.ui_update_latencies else 0
            
            # Calculate tick rate statistics
            current_rate = self.tick_rates[-1] if self.tick_rates else 0
            avg_rate = np.mean(self.tick_rates) if self.tick_rates else 0
            
            # Calculate memory statistics
            current_memory = self.memory_usage[-1] if self.memory_usage else 0
            avg_memory = np.mean(self.memory_usage) if self.memory_usage else 0
            
            # Calculate uptime
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            return {
                'websocket_latency_ms': ws_latency,
                'processing_latency_ms': proc_latency,
                'ui_latency_ms': ui_latency,
                'total_latency_ms': ws_latency + proc_latency + ui_latency,
                'current_tick_rate': current_rate,
                'average_tick_rate': avg_rate,
                'current_memory_mb': current_memory,
                'average_memory_mb': avg_memory,
                'uptime_seconds': uptime
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            return {
                'websocket_latency_ms': 0.0,
                'processing_latency_ms': 0.0,
                'ui_latency_ms': 0.0,
                'total_latency_ms': 0.0,
                'current_tick_rate': 0.0,
                'average_tick_rate': 0.0,
                'current_memory_mb': 0.0,
                'average_memory_mb': 0.0,
                'uptime_seconds': 0.0
            }
    
    def get_latency_percentiles(self) -> Dict[str, float]:
        """Calculate latency percentiles"""
        try:
            total_latencies = [w + p + u for w, p, u in zip(
                self.websocket_latencies,
                self.processing_latencies,
                self.ui_update_latencies
            )]
            
            if total_latencies:
                return {
                    'p50_latency_ms': np.percentile(total_latencies, 50),
                    'p90_latency_ms': np.percentile(total_latencies, 90),
                    'p99_latency_ms': np.percentile(total_latencies, 99)
                }
            
            return {
                'p50_latency_ms': 0.0,
                'p90_latency_ms': 0.0,
                'p99_latency_ms': 0.0
            }
            
        except Exception as e:
            logger.error(f"Error calculating latency percentiles: {str(e)}")
            return {
                'p50_latency_ms': 0.0,
                'p90_latency_ms': 0.0,
                'p99_latency_ms': 0.0
            }
    
    def reset(self):
        """Reset all metrics"""
        self.websocket_latencies.clear()
        self.processing_latencies.clear()
        self.ui_update_latencies.clear()
        self.tick_times.clear()
        self.tick_rates.clear()
        self.memory_usage.clear()
        self.start_time = datetime.now()
        logger.info("Performance metrics reset") 