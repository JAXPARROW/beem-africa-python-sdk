"""
OTP (One-Time Password) functionality for Beem Africa.
"""

from typing import Dict, Any, Optional
from .client import BeemClient
from .utils.validators import PhoneNumberValidator
from .exceptions import BeemValidationError


class OTPMixin:
    """OTP functionality mixin for BeemClient"""
    
    def send_otp(
        self: BeemClient,
        phone: str,
        app_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send OTP to a phone number.
        
        Args:
            phone: Recipient phone number
            app_id: Optional App ID (if not provided, uses default)
            
        Returns:
            Dict with pinId for verification
            
        Raises:
            BeemValidationError: Invalid phone number
            BeemAuthenticationError: Invalid credentials
        """
        # Validate and clean phone number
        cleaned = PhoneNumberValidator.clean(phone)
        
        # Prepare payload
        payload = {'msisdn': cleaned}
        if app_id:
            payload['app_id'] = app_id
        
        # Make request
        response = self.http.request('POST', 'public/v1/otp/send', json=payload)
        result = self._handle_response(response)
        
        return result['data']
    
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
        """
        payload = {
            'pinId': pin_id,
            'pin': pin
        }
        
        response = self.http.request('POST', 'public/v1/otp/verify', json=payload)
        result = self._handle_response(response)
        
        # Check if valid (code 117 means valid)
        data = result.get('data', {})
        message = data.get('message', {})
        return message.get('code') == 117