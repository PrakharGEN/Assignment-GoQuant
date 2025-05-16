import subprocess
import logging
import socket
import requests
from typing import Dict

logger = logging.getLogger(__name__)

class VPNHandler:
    def __init__(self):
        self.connected = False
        self.target_ip = "47.241.99.110"  # OKX API server
        
    def check_connection(self) -> Dict[str, bool]:
        """Check if VPN is connected and can reach OKX"""
        try:
            # Try to reach OKX server
            socket.create_connection((self.target_ip, 80), timeout=5)
            self.connected = True
            logger.info("VPN connection verified")
            return {"status": True, "message": "Connected to OKX network"}
        except (socket.timeout, socket.error) as e:
            self.connected = False
            logger.error(f"VPN connection failed: {str(e)}")
            return {"status": False, "message": "Cannot reach OKX network. Please check VPN connection"}
    
    def verify_api_access(self) -> bool:
        """Verify if we can access OKX API"""
        try:
            response = requests.get("https://www.okx.com/api/v5/public/time", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API access verification failed: {str(e)}")
            return False
    
    def get_connection_info(self) -> Dict[str, str]:
        """Get current connection information"""
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            if response.status_code == 200:
                return {
                    "ip": response.json()["ip"],
                    "vpn_status": "Connected" if self.connected else "Disconnected",
                    "api_access": "Available" if self.verify_api_access() else "Unavailable"
                }
        except Exception as e:
            logger.error(f"Error getting connection info: {str(e)}")
        
        return {
            "ip": "Unknown",
            "vpn_status": "Error",
            "api_access": "Unknown"
        } 