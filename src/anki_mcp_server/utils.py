"""
Utility functions for Anki-MCP-Server.

This module provides utility functions for error handling, data transformation,
and other common operations used throughout the application.
"""

import logging
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("anki_mcp_server")

T = TypeVar('T')

class AnkiConnectError(Exception):
    """Exception raised for Anki-Connect related errors"""
    def __init__(self, message: str, error_code: Optional[int] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ResourceError(Exception):
    """Exception raised for MCP Resource related errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ToolError(Exception):
    """Exception raised for MCP Tool related errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def format_error_message(error: Exception) -> str:
    """Format exception into user-friendly error message"""
    if isinstance(error, (AnkiConnectError, ResourceError, ToolError)):
        return error.message
    return str(error)

def validate_params(params: Dict[str, Any], required_params: List[str]) -> None:
    """
    Validate that all required parameters are present in the params dictionary
    
    Args:
        params: Dictionary of parameters
        required_params: List of required parameter names
        
    Raises:
        ResourceError: If any required parameter is missing
    """
    missing_params = [param for param in required_params if param not in params]
    if missing_params:
        raise ResourceError(f"Missing required parameters: {', '.join(missing_params)}")

def safe_call(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Safely call a function and handle any exceptions
    
    Args:
        func: Function to call
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The result of the function call
        
    Raises:
        ResourceError: If an exception occurs during the function call
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error calling {func.__name__}: {str(e)}")
        if isinstance(e, (AnkiConnectError, ResourceError, ToolError)):
            raise
        raise ResourceError(f"Error in {func.__name__}: {str(e)}")

# URI helpers
def build_resource_uri(base: str, *paths: str) -> str:
    """
    Build a resource URI by joining the base with additional path components
    
    Args:
        base: Base URI (e.g., "anki://")
        *paths: Additional path components to append
        
    Returns:
        Complete URI with all components joined
    """
    joined_path = "/".join(p.strip("/") for p in paths if p)
    return f"{base.rstrip('/')}/{joined_path}"

# Data transformation helpers
def transform_anki_connect_response(response: Dict[str, Any]) -> Any:
    """
    Transform Anki-Connect response into a more MCP-friendly format
    
    Args:
        response: Raw response from Anki-Connect
        
    Returns:
        Transformed response data
        
    Raises:
        AnkiConnectError: If the response contains an error
    """
    if response.get("error") is not None:
        raise AnkiConnectError(response["error"])
    return response.get("result") 