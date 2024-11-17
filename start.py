# start.py
import socket
import uvicorn
import logging
import sys
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_port_available(port: int) -> bool:
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', port))
        sock.close()
        return True
    except:
        return False

def clean_pycache():
    """Clean Python cache files"""
    logger.info("Cleaning __pycache__ directories...")
    root_dir = Path('.')
    for cache_dir in root_dir.rglob('__pycache__'):
        try:
            for cache_file in cache_dir.iterdir():
                cache_file.unlink()
            cache_dir.rmdir()
            logger.info(f"Cleaned {cache_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean {cache_dir}: {e}")

def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """Find an available port"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    raise RuntimeError("No available ports found")

def start_server():
    """Start the FastAPI server"""
    try:
        # Clean up cache
        clean_pycache()
        
        # Find available port
        port = find_available_port()
        logger.info(f"Starting server on port {port}")
        
        # Start server
        uvicorn.run(
            "src.app:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            reload_dirs=["src"]
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()