"""
Main Beem Africa client with connection pooling and health check.
"""

import logging
from typing import Optional, Dict, Any, Union, List

from .utils.http_client import PooledHTTPClient
from .utils.validators import PhoneNumberValidator
from .exceptions import (
    BeemError, BeemAuthenticationError, BeemAPIError,
    BeemRateLimitError, BeemServerError, BeemConnectionError
)


class BeemClient:
    """
    Main client for Beem Africa APIs.
    
    This client provides connection pooling, automatic retries, and
    comprehensive error handling for production use.
    
    Example:
        client = BeemClient(api_key="your_key", secret_key="your_secret")
        
        # Check if API is healthy
        if client.is_healthy():
            print("Beem API is accessible")
        
        # Send SMS
        response = client.send_sms(
            source_addr="NANOBILL",
            message="Hello world",
            recipients=["255755660639"]
        )
        
        # Close client when done
        client.close()
    """
    
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        timeout: int = 30,
        max_retries: int = 3,
        pool_connections: int = 10,
        pool_maxsize: int = 100,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Beem client with connection pooling.
        
        Args:
            api_key: Beem API key
            secret_key: Beem secret key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum number of connections to keep alive
            logger: Custom logger instance
        """
        self.api_key = api_key
        self.secret_key = secret_key
        
        # Initialize HTTP client with connection pooling
        self.http = PooledHTTPClient(
            api_key=api_key,
            secret_key=secret_key,
            base_url="https://apisms.beem.africa",
            timeout=timeout,
            max_retries=max_retries,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            logger=logger
        )
        
        # Separate base URL for delivery reports
        self.dlr_base_url = "https://dlrapi.beem.africa"
        
        self.logger = logger or logging.getLogger(__name__)
    
    def is_healthy(self) -> bool:
        """
        Check if Beem API is accessible and credentials are valid.
        
        This method never raises exceptions, always returns a boolean.
        Perfect for monitoring and health checks.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            # Use balance endpoint as lightweight health check
            response = self.http.request(
                'GET',
                'public/v1/vendors/balance',
                timeout=5.0  # Short timeout for health check
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _handle_response(self, response, expected_status=200):
        """
        Handle HTTP response and convert errors to appropriate exceptions.
        """
        if response.status_code == expected_status:
            return response.json()
        
        # Handle error status codes
        error_map = {
            401: BeemAuthenticationError,
            429: BeemRateLimitError,
        }
        
        if response.status_code in error_map:
            raise error_map[response.status_code](
                f"HTTP {response.status_code}: {response.text}"
            )
        elif 500 <= response.status_code < 600:
            raise BeemServerError(
                f"Beem server error: {response.status_code}",
                code=response.status_code
            )
        else:
            # Try to parse Beem-specific error codes
            try:
                error_data = response.json()
                code = error_data.get('code')
                message = error_data.get('message', response.text)
                
                if code == 111:
                    from .exceptions import BeemInvalidSenderError
                    raise BeemInvalidSenderError(message, code=code)
                elif code == 112:
                    from .exceptions import BeemInsufficientBalanceError
                    raise BeemInsufficientBalanceError(message, code=code)
                else:
                    raise BeemAPIError(message, code=code, response_data=error_data)
            except ValueError:
                # Not JSON
                raise BeemAPIError(f"HTTP {response.status_code}: {response.text}")
    
    def close(self):
        """Close the HTTP client and free resources."""
        self.http.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()