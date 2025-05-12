"""
Configuration module for Anki-MCP-Server.

This module manages configuration settings for the server, including
Anki-Connect connection parameters and MCP server settings.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AnkiConnectConfig(BaseModel):
    """Configuration settings for Anki-Connect"""
    url: str = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
    api_key: Optional[str] = os.getenv("ANKI_CONNECT_API_KEY")
    timeout: float = float(os.getenv("ANKI_CONNECT_TIMEOUT", "30.0"))
    version: int = int(os.getenv("ANKI_CONNECT_VERSION", "6"))

class MCPServerConfig(BaseModel):
    log_level: str = os.getenv("LOG_LEVEL", "info")

# Main configuration class that includes all sub-configurations
class Config(BaseModel):
    """Main configuration class for Anki-MCP-Server"""
    anki_connect: AnkiConnectConfig = AnkiConnectConfig()
    mcp_server: MCPServerConfig = MCPServerConfig()
    
    # Application paths
    base_dir: Path = Path(__file__).parent.parent.parent

# Create a global configuration instance
config = Config() 