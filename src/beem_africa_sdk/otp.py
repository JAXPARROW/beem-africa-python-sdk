"""
OTP (One-Time Password) functionality for Beem Africa.
"""

from typing import Dict, Any, Optional
from .client import BeemClient
from .utils.validators import PhoneNumberValidator
from .exceptions import BeemValidationError, BeemAPIError


class OTPMixin:
    """OTP functionality mixin for BeemClient"""
    
    def send_otp(
        self: BeemClient,
        phone: str,
        app_id: Optional[str] = None,
        sender_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send OTP to a phone number.
        
        Note: OTP service may not be available on all Beem accounts.
        Contact Beem support to enable OTP functionality.
        
        Args:
            phone: Recipient phone number
            app_id: Optional Application ID (if not provided, uses default)
            sender_id: Optional Sender ID for the OTP message (max 11 characters).
                      If not provided, uses first approved sender ID.
            
        Returns:
            Dict with pinId for verification
            
        Raises:
            BeemValidationError: Invalid phone number or sender ID
            BeemAPIError: OTP service not available or API error
            BeemAuthenticationError: Invalid credentials
        """
        # Validate and clean phone number
        cleaned = PhoneNumberValidator.clean(phone)
        
        # Use approved sender if none provided
        if sender_id is None and self._approved_senders:
            sender_id = self._approved_senders[0]
        
        # Validate sender ID if provided
        if sender_id:
            if len(sender_id) > 11:
                raise BeemValidationError(
                    f"Sender ID must be 11 characters or less, got {len(sender_id)}"
                )
        
        # Prepare payload (use appId as per API docs)
        payload = {'msisdn': cleaned}
        if app_id:
            payload['appId'] = app_id
        
        # Note: sender_id is not used in the current OTP API
        # It's handled at the application level in Beem
        
        try:
            # Create OTP-specific HTTP client with OTP credentials
            from .utils.http_client import PooledHTTPClient
            
            otp_http = PooledHTTPClient(
                api_key=self.otp_api_key,
                secret_key=self.otp_secret_key,
                base_url="https://apiotp.beem.africa/v1",
                timeout=self.http.timeout,
                max_retries=3,  # Default value since not stored
                pool_connections=10,  # Default values
                pool_maxsize=100,
                logger=self.http.logger
            )
            
            try:
                # Make request to /request endpoint
                response = otp_http.request('POST', 'request', json=payload)
                result = self._handle_response(response)
                
                return result['data']
            finally:
                otp_http.close()
                
        except BeemAPIError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise BeemAPIError(
                    "OTP service is not available on this Beem account. "
                    "Please contact Beem support to enable OTP functionality.",
                    response=None
                ) from e
            raise
    
    def verify_otp(self, pin_id: str, pin: str) -> bool:
        """
        Verify OTP code.
        
        Args:
            pin_id: Pin ID from send_otp response
            pin: OTP code entered by user
            
        Returns:
            True if OTP is valid, False otherwise
            
        Raises:
            BeemAuthenticationError: Invalid credentials
            BeemAPIError: OTP verification failed
        """
        payload = {
            'pinId': pin_id,
            'pin': pin
        }
        
        try:
            # Create OTP-specific HTTP client with OTP credentials
            from .utils.http_client import PooledHTTPClient
            
            otp_http = PooledHTTPClient(
                api_key=self.otp_api_key,
                secret_key=self.otp_secret_key,
                base_url="https://apiotp.beem.africa/v1",
                timeout=self.http.timeout,
                max_retries=3,  # Default value since not stored
                pool_connections=10,  # Default values
                pool_maxsize=100,
                logger=self.http.logger
            )
            
            try:
                response = otp_http.request('POST', 'verify', json=payload)
                result = self._handle_response(response)
                
                # Check if valid (code 117 means valid)
                data = result.get('data', {})
                message = data.get('message', {})
                return message.get('code') == 117
            finally:
                otp_http.close()
                
        except BeemAPIError as e:
            # For verification errors, check the response if available
            # Code 114 = Incorrect Pin, 115 = Pin Timeout, 116 = Attempts Exceeded
            error_data = getattr(e, 'response_data', None)
            if error_data and 'data' in error_data:
                data = error_data['data']
                message = data.get('message', {})
                code = message.get('code')
                if code in [114, 115, 116]:
                    return False
            
            raise