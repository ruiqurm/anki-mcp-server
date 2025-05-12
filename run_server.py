#!/usr/bin/env python
"""
Run script for Anki MCP Server.

This script provides a simple command-line interface to start the Anki MCP Server.
"""

import argparse
import logging
import sys
from src.anki_mcp_server import run_server, config

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Anki MCP Server")
    parser.add_argument(
        "--log-level", 
        choices=["debug", "info", "warning", "error", "critical"],
        help=f"Log level (default: {config.mcp_server.log_level})",
        default=config.mcp_server.log_level
    )
    parser.add_argument(
        "--anki-connect-url", 
        help=f"Anki-Connect URL (default: {config.anki_connect.url})",
        default=config.anki_connect.url
    )
    
    return parser.parse_args()

def clean_proxy():
    import os
    if 'http_proxy' in os.environ:
        del os.environ['http_proxy']
        print("http_proxy 环境变量已取消")
    elif 'HTTP_PROXY' in os.environ:
        del os.environ['HTTP_PROXY']
        print("HTTP_PROXY 环境变量已取消")
    else:
        print("http_proxy 或 HTTP_PROXY 环境变量未设置")

    if 'https_proxy' in os.environ:
        del os.environ['https_proxy']
        print("https_proxy 环境变量已取消")
    elif 'HTTPS_PROXY' in os.environ:
        del os.environ['HTTPS_PROXY']
        print("HTTPS_PROXY 环境变量已取消")
    else:
        print("https_proxy 或 HTTPS_PROXY 环境变量未设置")

def main():
    """Main entry point"""
    args = parse_args()
    
    # Update config with command line arguments
    config.mcp_server.log_level = args.log_level
    config.anki_connect.url = args.anki_connect_url
 
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    clean_proxy()
    # Start the server
    try:
        run_server()
        return 0
    except Exception as e:
        logging.error(f"Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 