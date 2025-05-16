import psutil
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import sys
import threading
from collections import deque
import logging
import platform

class EnhancedPerformanceCollector:
    def __init__(self, target_pid=None, duration=60):
        self.duration = duration
        self.target_pid = target_pid
        self.output_dir = "docs/performance_data"
        self.is_windows = platform.system() == 'Windows'
        
        # Basic metrics
        self.timestamps = []
        self.cpu_usage = []
        self.memory_usage = []
        
        # Thread metrics
        self.thread_usage = {}
        
        # System-wide network metrics (for Windows compatibility)
        self.network_usage = []
        self.bandwidth_usage = []
        
        # Storage metrics
        self.disk_read_bytes = []
        self.disk_write_bytes = []
        
        # Create output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Setup logging
        logging.basicConfig(
            filename=f"{self.output_dir}/collector.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def collect_basic_metrics(self, process):
        """Collect CPU and memory metrics"""
        try:
            self.timestamps.append(time.time() - self.start_time)
            self.cpu_usage.append(process.cpu_percent())
            self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        except Exception as e:
            logging.error(f"Error collecting basic metrics: {str(e)}")
        
    def collect_thread_metrics(self, process):
        """Collect thread-specific metrics"""
        try:
            threads = process.threads()
            for thread in threads:
                if thread.id not in self.thread_usage:
                    self.thread_usage[thread.id] = []
                self.thread_usage[thread.id].append(thread.system_time + thread.user_time)
        except Exception as e:
            logging.error(f"Error collecting thread metrics: {str(e)}")
    
    def collect_network_metrics(self):
        """Collect system-wide network metrics (Windows compatible)"""
        try:
            net_io = psutil.net_io_counters()
            self.network_usage.append((net_io.bytes_sent + net_io.bytes_recv) / 1024)  # KB
            self.bandwidth_usage.append(net_io.bytes_sent / 1024)  # KB/s
        except Exception as e:
            logging.error(f"Error collecting network metrics: {str(e)}")
    
    def collect_storage_metrics(self, process):
        """Collect disk I/O metrics"""
        try:
            if hasattr(process, 'io_counters'):
                io_counters = process.io_counters()
                self.disk_read_bytes.append(io_counters.read_bytes / 1024)  # KB
                self.disk_write_bytes.append(io_counters.write_bytes / 1024)  # KB
            else:
                # Use system-wide disk I/O as fallback
                disk_io = psutil.disk_io_counters()
                self.disk_read_bytes.append(disk_io.read_bytes / 1024)  # KB
                self.disk_write_bytes.append(disk_io.write_bytes / 1024)  # KB
        except Exception as e:
            logging.error(f"Error collecting storage metrics: {str(e)}")
    
    def collect_metrics(self):
        self.start_time = time.time()
        try:
            process = psutil.Process(self.target_pid) if self.target_pid else psutil.Process()
            logging.info(f"Monitoring process with PID: {process.pid}")
            
            while time.time() - self.start_time < self.duration:
                try:
                    self.collect_basic_metrics(process)
                    self.collect_thread_metrics(process)
                    self.collect_network_metrics()  # System-wide network metrics
                    self.collect_storage_metrics(process)
                    time.sleep(0.1)  # Sample every 100ms
                    
                except psutil.NoSuchProcess:
                    logging.error(f"Process {self.target_pid} has terminated.")
                    break
                except Exception as e:
                    logging.error(f"Error collecting metrics: {str(e)}")
                    
        except psutil.NoSuchProcess:
            logging.error(f"Process with PID {self.target_pid} not found!")
            return
    
    def calculate_statistics(self):
        """Calculate various statistics from collected data"""
        stats = {
            "cpu": {
                "average": np.mean(self.cpu_usage) if self.cpu_usage else 0,
                "peak": np.max(self.cpu_usage) if self.cpu_usage else 0,
                "pattern": "Stable" if self.cpu_usage and np.std(self.cpu_usage) < 5 else "Variable"
            },
            "memory": {
                "average": np.mean(self.memory_usage) if self.memory_usage else 0,
                "peak": np.max(self.memory_usage) if self.memory_usage else 0,
                "growth_rate": (self.memory_usage[-1] - self.memory_usage[0])/self.duration if self.memory_usage else 0
            },
            "network": {
                "average_bandwidth": np.mean(self.bandwidth_usage) if self.bandwidth_usage else 0,
                "peak_bandwidth": np.max(self.bandwidth_usage) if self.bandwidth_usage else 0,
                "total_transfer": np.sum(self.network_usage) if self.network_usage else 0
            },
            "storage": {
                "total_read": (self.disk_read_bytes[-1] - self.disk_read_bytes[0])/1024 if self.disk_read_bytes else 0,
                "total_write": (self.disk_write_bytes[-1] - self.disk_write_bytes[0])/1024 if self.disk_write_bytes else 0
            } if self.disk_read_bytes and self.disk_write_bytes else {"total_read": 0, "total_write": 0}
        }
        return stats
    
    def generate_enhanced_report(self):
        stats = self.calculate_statistics()
        report = f"""# Enhanced Performance Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Performance Metrics

### 1. CPU Utilization
- Average CPU Usage: {stats['cpu']['average']:.2f}%
- Peak CPU Usage: {stats['cpu']['peak']:.2f}%
- Usage Pattern: {stats['cpu']['pattern']}
- Thread Count: {len(self.thread_usage)}

### 2. Memory Usage
- Average Memory Usage: {stats['memory']['average']:.2f} MB
- Peak Memory Usage: {stats['memory']['peak']:.2f} MB
- Memory Growth Rate: {stats['memory']['growth_rate']:.2f} MB/s

### 3. Network Performance (System-wide)
- Average Bandwidth: {stats['network']['average_bandwidth']:.2f} KB/s
- Peak Bandwidth: {stats['network']['peak_bandwidth']:.2f} KB/s
- Total Data Transfer: {stats['network']['total_transfer']:.2f} KB

### 4. Storage Activity
- Total Read: {stats['storage']['total_read']:.2f} MB
- Total Write: {stats['storage']['total_write']:.2f} MB

## Thread Analysis
"""
        # Add thread-specific information
        for thread_id, usage in self.thread_usage.items():
            report += f"- Thread {thread_id}: {np.mean(usage):.2f}% average CPU\n"
        
        report += "\n## Performance Visualizations\n"
        report += "![CPU Usage](cpu_usage.png)\n"
        report += "![Memory Usage](memory_usage.png)\n"
        report += "![Network Usage](network_usage.png)\n"
        
        with open(f"{self.output_dir}/enhanced_performance_report.md", 'w') as f:
            f.write(report)
    
    def generate_plots(self):
        # CPU Usage Plot
        if self.cpu_usage:
            plt.figure(figsize=(10, 6))
            plt.plot(self.timestamps, self.cpu_usage)
            plt.title('CPU Usage Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('CPU Usage (%)')
            plt.grid(True)
            plt.savefig(f"{self.output_dir}/cpu_usage.png")
            plt.close()
        
        # Memory Usage Plot
        if self.memory_usage:
            plt.figure(figsize=(10, 6))
            plt.plot(self.timestamps, self.memory_usage)
            plt.title('Memory Usage Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Memory Usage (MB)')
            plt.grid(True)
            plt.savefig(f"{self.output_dir}/memory_usage.png")
            plt.close()
        
        # Network Usage Plot
        if self.bandwidth_usage:
            plt.figure(figsize=(10, 6))
            plt.plot(self.timestamps, self.bandwidth_usage)
            plt.title('Network Bandwidth Usage Over Time')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Bandwidth (KB/s)')
            plt.grid(True)
            plt.savefig(f"{self.output_dir}/network_usage.png")
            plt.close()

def main():
    target_pid = int(sys.argv[1]) if len(sys.argv) > 1 else None
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 300  # 5 minutes default
    
    collector = EnhancedPerformanceCollector(target_pid=target_pid, duration=duration)
    print(f"Starting enhanced performance data collection{f' for PID {target_pid}' if target_pid else ''}...")
    collector.collect_metrics()
    
    if collector.timestamps:  # Only generate reports if we collected data
        print("Generating performance plots...")
        collector.generate_plots()
        print("Generating enhanced performance report...")
        collector.generate_enhanced_report()
        print("Performance analysis completed!")
    else:
        print("No data was collected. Exiting.")

if __name__ == "__main__":
    main() 