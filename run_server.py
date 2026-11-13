"""
Server Launcher for Hưng Phát Multi-Agent Dashboard.
"""

import sys
from src.web.app import start_server

if __name__ == "__main__":
    port = 8088
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    start_server(port)

