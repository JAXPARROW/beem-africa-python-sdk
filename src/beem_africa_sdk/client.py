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
        client = BeemClient(
            api_key="your_sms_key", 
            secret_key="your_sms_secret",
            otp_api_key="your_otp_key",  # Optional: separate OTP credentials
            otp_secret_key="your_otp_secret"
        )
        
        # Check if API is healthy
        if client.is_healthy():
            print("Beem API is accessible")
        
        # Send SMS
        response = client.send_sms(
            source_addr="NANOBILL",
            message="Hello world",
            recipients=["255755660639"]
        )
        
        # Send OTP (uses OTP credentials if provided)
        otp_data = client.send_otp("255755660639", app_id="4147")
        
        # Close client when done
        client.close()
    """
    
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        otp_api_key: Optional[str] = None,
        otp_secret_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        pool_connections: int = 10,
        pool_maxsize: int = 100,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Beem client with connection pooling.
        
        Args:
            api_key: Beem SMS API key
            secret_key: Beem SMS secret key
            otp_api_key: Beem OTP API key (if different from SMS)
            otp_secret_key: Beem OTP secret key (if different from SMS)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum number of connections to keep alive
            logger: Custom logger instance
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.otp_api_key = otp_api_key or api_key
        self.otp_secret_key = otp_secret_key or secret_key
        
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
        
        # Approved sender IDs (can be set by user or retrieved from API)
        self._approved_senders: List[str] = []
        
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
    
    def set_approved_senders(self, senders: List[str]) -> None:
        """
        Set the list of approved sender IDs for this account.
        
        Args:
            senders: List of approved sender ID strings (max 11 chars each)
            
        Raises:
            BeemValidationError: If any sender ID is invalid
        """
        for sender in senders:
            if not sender or len(sender) > 11:
                raise BeemValidationError(
                    f"Sender ID must be 1-11 characters, got '{sender}' ({len(sender)} chars)"
                )
        self._approved_senders = senders.copy()
    
    def get_approved_senders(self) -> List[str]:
        """
        Get the list of approved sender IDs for this account.
        
        Returns:
            List of approved sender ID strings
        """
        return self._approved_senders.copy()
    
    def add_approved_sender(self, sender: str) -> None:
        """
        Add a single approved sender ID.
        
        Args:
            sender: Sender ID to add (max 11 characters)
            
        Raises:
            BeemValidationError: If sender ID is invalid
        """
        if not sender or len(sender) > 11:
            raise BeemValidationError(
                f"Sender ID must be 1-11 characters, got '{sender}' ({len(sender)} chars)"
            )
        if sender not in self._approved_senders:
            self._approved_senders.append(sender)
    
    def validate_sender_id(self, sender_id: str) -> bool:
        """
        Validate if a sender ID is approved by attempting a test SMS.
        
        This method sends a test SMS with minimal content to check if the
        sender ID is approved. Note: This will consume SMS credits.
        
        Args:
            sender_id: Sender ID to validate
            
        Returns:
            True if sender ID is approved, False otherwise
            
        Raises:
            BeemValidationError: Invalid sender ID format
        """
        if not sender_id or len(sender_id) > 11:
            raise BeemValidationError(
                f"Sender ID must be 1-11 characters, got '{sender_id}' ({len(sender_id)} chars)"
            )
        
        try:
            # Send a test SMS with minimal content
            response = self.http.request('POST', 'public/v1/send', json={
                'source_addr': sender_id,
                'message': 'Test',
                'recipients': ['255755660639']  # Use a test number
            })
            return response.status_code == 200
        except Exception:
            return False
    
    def close(self):
        """Close the HTTP client and free resources."""
        self.http.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()