import logging
import asyncio
import tkinter as tk
from src.ui.main_window import MainWindow
from src.utils.vpn_handler import VPNHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Check VPN connection first
    vpn_handler = VPNHandler()
    vpn_status = vpn_handler.check_connection()
    
    if not vpn_status["status"]:
        print(f"VPN Error: {vpn_status['message']}")
        return
    
    # Create main window
    root = MainWindow()
    
    # Create async event loop for tkinter
    async def update_gui():
        while True:
            root.update()
            await asyncio.sleep(1/60)  # 60 FPS
    
    # Run GUI and WebSocket client together
    await update_gui()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Error: {str(e)}") 