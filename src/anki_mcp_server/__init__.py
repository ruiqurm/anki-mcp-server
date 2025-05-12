"""
Anki MCP Server - A FastMCP-based server for Anki integration.

This package provides a Model Context Protocol (MCP) server for interacting with Anki
via the Anki-Connect plugin.
"""

from .server import mcp, run_server
from .config import config
from .utils import AnkiConnectError, ResourceError, ToolError
from .anki_connect_client import AsyncAnkiConnectClient, get_client
from .model import *

__version__ = "0.1.0"
__all__ = [
    "mcp", 
    "run_server", 
    "config", 
    "AnkiConnectError", 
    "ResourceError", 
    "ToolError",
    "AsyncAnkiConnectClient",
    "get_client",
    "FindCardsParams",
    "FindNotesParams",
    "FindDecksParams",
    "FindModelsParams",
    "FindNotesParams",
    "FindDecksParams",
    "FindModelsParams",
]
