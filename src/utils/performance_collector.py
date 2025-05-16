import psutil
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import sys

class PerformanceCollector:
    def __init__(self, target_pid=None, duration=60):  # Default 60 seconds
        self.duration = duration
        self.target_pid = target_pid
        self.timestamps = []
        self.cpu_usage = []
        self.memory_usage = []
        self.output_dir = "docs/performance_data"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def collect_metrics(self):
        start_time = time.time()
        try:
            # If target_pid is provided, monitor that process, otherwise monitor self
            process = psutil.Process(self.target_pid) if self.target_pid else psutil.Process()
            print(f"Monitoring process with PID: {process.pid}")
        except psutil.NoSuchProcess:
            print(f"Error: Process with PID {self.target_pid} not found!")
            return
        
        while time.time() - start_time < self.duration:
            try:
                self.timestamps.append(time.time() - start_time)
                self.cpu_usage.append(process.cpu_percent())
                self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
                time.sleep(0.1)  # Sample every 100ms
            except psutil.NoSuchProcess:
                print(f"Process {self.target_pid} has terminated.")
                break
    
    def generate_plots(self):
        # CPU Usage Plot
        plt.figure(figsize=(10, 6))
        plt.plot(self.timestamps, self.cpu_usage)
        plt.title('CPU Usage Over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel('CPU Usage (%)')
        plt.grid(True)
        plt.savefig(f"{self.output_dir}/cpu_usage.png")
        plt.close()
        
        # Memory Usage Plot
        plt.figure(figsize=(10, 6))
        plt.plot(self.timestamps, self.memory_usage)
        plt.title('Memory Usage Over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Memory Usage (MB)')
        plt.grid(True)
        plt.savefig(f"{self.output_dir}/memory_usage.png")
        plt.close()
        
        # Combined Metrics Plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        ax1.plot(self.timestamps, self.cpu_usage, 'b-', label='CPU Usage')
        ax1.set_ylabel('CPU Usage (%)')
        ax1.grid(True)
        ax1.legend()
        
        ax2.plot(self.timestamps, self.memory_usage, 'r-', label='Memory Usage')
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Memory Usage (MB)')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/combined_metrics.png")
        plt.close()
    
    def generate_report(self):
        avg_cpu = np.mean(self.cpu_usage)
        max_cpu = np.max(self.cpu_usage)
        avg_memory = np.mean(self.memory_usage)
        max_memory = np.max(self.memory_usage)
        
        report = f"""# Real Performance Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Metrics

### CPU Usage
- Average CPU Usage: {avg_cpu:.2f}%
- Peak CPU Usage: {max_cpu:.2f}%
- CPU Usage Pattern: {'Stable' if np.std(self.cpu_usage) < 5 else 'Variable'}

### Memory Usage
- Average Memory Usage: {avg_memory:.2f} MB
- Peak Memory Usage: {max_memory:.2f} MB
- Memory Growth Rate: {(self.memory_usage[-1] - self.memory_usage[0])/self.duration:.2f} MB/s

## Performance Visualizations
![CPU Usage](cpu_usage.png)
![Memory Usage](memory_usage.png)
![Combined Metrics](combined_metrics.png)
"""
        
        with open(f"{self.output_dir}/performance_report.md", 'w') as f:
            f.write(report)

def main():
    # Check if PID was provided as command line argument
    target_pid = int(sys.argv[1]) if len(sys.argv) > 1 else None
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 300  # 5 minutes default
    
    collector = PerformanceCollector(target_pid=target_pid, duration=duration)
    print(f"Starting performance data collection{f' for PID {target_pid}' if target_pid else ''}...")
    collector.collect_metrics()
    
    if collector.timestamps:  # Only generate reports if we collected data
        print("Generating performance plots...")
        collector.generate_plots()
        print("Generating performance report...")
        collector.generate_report()
        print("Performance analysis completed!")
    else:
        print("No data was collected. Exiting.")

if __name__ == "__main__":
    main() 