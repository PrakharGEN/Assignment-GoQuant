import subprocess
import sys
import time
import signal
import os
from datetime import datetime

def start_main_application():
    """Start the main application process."""
    process = subprocess.Popen([sys.executable, 'src/main.py'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    return process

def start_performance_collector(target_pid, duration=300):
    """Start the performance collector process."""
    return subprocess.Popen([sys.executable, 'src/utils/performance_collector.py', str(target_pid), str(duration)],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

def monitor_processes(collector_process, main_process):
    """Monitor both processes and handle their output."""
    try:
        while True:
            # Check if either process has terminated
            if collector_process.poll() is not None:
                print("Performance collector has stopped!")
                break
            if main_process.poll() is not None:
                print("Main application has stopped!")
                break
            
            # Print output from both processes
            collector_output = collector_process.stdout.readline()
            if collector_output:
                print(f"Collector: {collector_output.decode().strip()}")
            
            main_output = main_process.stdout.readline()
            if main_output:
                print(f"Main App: {main_output.decode().strip()}")
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nReceived interrupt signal. Shutting down gracefully...")
    finally:
        # Ensure both processes are terminated
        for process in [collector_process, main_process]:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

def main():
    print(f"Starting performance analysis session at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ensure the performance data directory exists
    os.makedirs("docs/performance_data", exist_ok=True)
    
    # Start main application first
    main_process = start_main_application()
    print(f"Started main application (PID: {main_process.pid})...")
    
    time.sleep(2)  # Give main app a moment to initialize
    
    # Start performance collector with main app's PID
    collector_process = start_performance_collector(main_process.pid)
    print("Started performance collector...")
    
    # Monitor and handle process output
    monitor_processes(collector_process, main_process)
    
    print(f"\nSession completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Performance data has been saved to docs/performance_data/")

if __name__ == "__main__":
    main() 