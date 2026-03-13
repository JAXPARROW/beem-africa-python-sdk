"""
HTTP client with connection pooling and retry logic.
This is the foundation for all API calls.
"""

import logging
import time
from typing import Optional, Dict, Any, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class PooledHTTPClient:
    """
    HTTP client with connection pooling, retries, and configurable timeouts.
    
    This client is designed to be reused across multiple requests to maximize
    performance and minimize resource usage.
    """
    
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        base_url: str = "https://apisms.beem.africa",
        timeout: int = 30,
        max_retries: int = 3,
        pool_connections: int = 10,
        pool_maxsize: int = 100,
        backoff_factor: float = 0.5,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the HTTP client with connection pooling.
        
        Args:
            api_key: Beem API key
            secret_key: Beem secret key
            base_url: Base URL for API endpoints
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum number of connections to keep alive
            backoff_factor: Backoff factor for retries (waits = backoff_factor * (2 ** (retry - 1)))
            logger: Custom logger instance (optional)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        # Create session with connection pooling
        self.session = requests.Session()
        
        # Set basic authentication
        self.session.auth = (api_key, secret_key)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Beem-Python-SDK/0.1.0'
        })
        
        # Mount adapters with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            pool_block=False
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.logger.debug(f"HTTP client initialized with pool_connections={pool_connections}, pool_maxsize={pool_maxsize}")
    
    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request with automatic retry and error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be appended to base_url)
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
            
        Raises:
            BeemConnectionError: On network issues
            Various BeemAPIError subclasses based on response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Set default timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        self.logger.debug(f"Making {method} request to {url}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.debug(f"Response status: {response.status_code}")
            return response
            
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request timeout: {e}")
            raise BeemConnectionError(f"Request timeout after {self.timeout}s")
            
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise BeemConnectionError(f"Failed to connect to Beem API: {e}")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise BeemConnectionError(f"Request failed: {e}")
    
    def close(self):
        """Close the session and free resources."""
        self.session.close()
        self.logger.debug("HTTP client closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()