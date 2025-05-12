"""
Asynchronous Anki-Connect client module for communicating with Anki.

This module provides an asynchronous client for interacting with the Anki-Connect API.
It focuses on operations related to decks, notes, models, and cards.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union, TypeVar, cast

import httpx
from pydantic import BaseModel

from .config import config
from .utils import AnkiConnectError, transform_anki_connect_response

logger = logging.getLogger(__name__)

T = TypeVar('T')

class AsyncAnkiConnectClient:
    """
    Asynchronous client for interacting with the Anki-Connect API.
    
    This class provides asynchronous methods for sending requests to Anki-Connect
    and handling the responses, with a focus on deck, note, model, and card operations.
    """
    
    def __init__(
        self, 
        url: Optional[str] = None, 
        api_key: Optional[str] = None,
        version: Optional[int] = None,
        timeout: Optional[float] = None
    ):
        """
        Initialize the asynchronous Anki-Connect client.
        
        Args:
            url: The URL of the Anki-Connect server, defaults to config value
            api_key: The API key for authentication, defaults to config value
            version: The API version to use, defaults to config value
            timeout: Request timeout in seconds, defaults to config value
        """
        self.url = url or config.anki_connect.url
        self.api_key = api_key or config.anki_connect.api_key
        self.version = version or config.anki_connect.version
        self.timeout = timeout or config.anki_connect.timeout
        
        # Initialize async HTTP client - will be set in __aenter__
        self.client: Optional[httpx.AsyncClient] = None
        
        logger.info(f"Initialized async Anki-Connect client with URL: {self.url}")
    
    async def __aenter__(self):
        """Async context manager enter - creates the AsyncClient"""
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - closes the AsyncClient"""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def _ensure_client(self):
        """Ensure the async client is initialized"""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def request(self, action: str, model: Optional[BaseModel] = None) -> Any:
        """
        Send an asynchronous request to Anki-Connect.
        
        Args:
            action: The action to perform
            model: A Pydantic model containing the parameters, optional for some actions
            
        Returns:
            The result of the action
            
        Raises:
            AnkiConnectError: If the request fails or Anki-Connect returns an error
        """
        await self._ensure_client()
        
        request_data = {
            "action": action,
            "version": self.version,
        }
        
        if model:
            request_data["params"] = model.model_dump(exclude_none=True)
            
        if self.api_key:
            request_data["key"] = self.api_key
            
        logger.debug(f"Sending async request to Anki-Connect: {action}")
        
        try:
            assert self.client is not None  # Helps type checking know client is initialized
            response = await self.client.post(
                self.url,
                content=json.dumps(request_data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            # Check for API-level errors
            return transform_anki_connect_response(result)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Anki-Connect: {e}")
            raise AnkiConnectError(f"Anki-Connect returned HTTP error: {e}")
        except httpx.RequestError as e:
            logger.error(f"Network error communicating with Anki-Connect: {e}")
            raise AnkiConnectError(f"Failed to connect to Anki-Connect: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in Anki-Connect response: {e}")
            raise AnkiConnectError("Invalid response from Anki-Connect")
            
    async def check_connection(self) -> bool:
        """
        Check if the connection to Anki-Connect is working.
        
        Returns:
            True if the connection is working, False otherwise
        """
        try:
            version = await self.request("version")
            logger.info(f"Connected to Anki-Connect version: {version}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Anki-Connect: {e}")
            return False
            
    async def close(self):
        """Close the HTTP client if it's open"""
        if self.client:
            await self.client.aclose()
            self.client = None
async def get_client() -> AsyncAnkiConnectClient:
    """
    Get the singleton async client instance.
    
    Returns:
        A configured AsyncAnkiConnectClient instance
    """
    client = AsyncAnkiConnectClient()
    await client._ensure_client()
    return client 