"""
SMS functionality for Beem Africa.
"""

from typing import Union, List, Dict, Any, Optional
from .client import BeemClient
from .utils.validators import PhoneNumberValidator
from .exceptions import BeemValidationError


class SMSMixin:
    """SMS functionality mixin for BeemClient"""
    
    def send_sms(
        self: BeemClient,
        message: str,
        recipients: Union[str, List[str]],
        source_addr: Optional[str] = None,
        schedule_time: str = "",
        encoding: str = "0"
    ) -> Dict[str, Any]:
        """
        Send SMS to one or multiple recipients.
        
        Note: Beem API does not support Unicode characters (emojis, special symbols).
        Messages containing Unicode will be rejected. Use plain ASCII text only.
        
        Args:
            message: SMS content (plain ASCII text only, no Unicode/emojis)
            recipients: Single phone number or list of phone numbers
            source_addr: Sender ID (max 11 characters, alphanumeric). 
                        If not provided, uses first approved sender ID.
            schedule_time: Optional schedule time (format: "yyyy-mm-dd hh:mm", UTC)
            encoding: Message encoding (default: "0" for plain text)
            
        Returns:
            Dict with API response containing request_id and stats
            
        Raises:
            BeemValidationError: Invalid input parameters
            BeemInvalidSenderError: Sender ID not approved
            BeemInsufficientBalanceError: Not enough credit
            BeemAuthenticationError: Invalid credentials
        """
        # Use approved sender if none provided
        if source_addr is None:
            if self._approved_senders:
                source_addr = self._approved_senders[0]
            else:
                raise BeemValidationError(
                    "No sender ID provided and no approved senders configured. "
                    "Use set_approved_senders() to configure sender IDs or provide source_addr explicitly."
                )
        
        # Validate sender ID
        if not source_addr or len(source_addr) > 11:
            raise BeemValidationError(
                f"Sender ID must be 1-11 characters, got {len(source_addr)}"
            )
        
        # Normalize recipients to list
        if isinstance(recipients, str):
            recipients = [recipients]
        
        if not recipients:
            raise BeemValidationError("At least one recipient required")
        
        # Validate and clean phone numbers
        cleaned_recipients = []
        for i, phone in enumerate(recipients):
            try:
                cleaned = PhoneNumberValidator.clean(phone)
                cleaned_recipients.append({
                    'recipient_id': str(i + 1),
                    'dest_addr': cleaned
                })
            except ValueError as e:
                raise BeemValidationError(f"Invalid phone number '{phone}': {e}")
        
        # Prepare request payload
        payload = {
            "source_addr": source_addr,
            "encoding": encoding,
            "message": message,
            "recipients": cleaned_recipients
        }
        
        if schedule_time:
            payload["schedule_time"] = schedule_time
        
        # Make request
        response = self.http.request('POST', 'v1/send', json=payload)
        result = self._handle_response(response)
        
        return result
    
    def get_balance(self) -> float:
        """
        Get current SMS credit balance.
        
        Returns:
            float: Current credit balance
            
        Raises:
            BeemAuthenticationError: Invalid credentials
            BeemConnectionError: Network error
        """
        response = self.http.request('GET', 'public/v1/vendors/balance')
        result = self._handle_response(response)
        return float(result['data']['credit_balance'])
    
    def get_delivery_report(self, dest_addr: str, request_id: str) -> List[Dict]:
        """
        Get delivery status for a sent message.
        
        Should be called at least 5 minutes after sending.
        
        Args:
            dest_addr: Destination phone number
            request_id: Request ID from send_sms response
            
        Returns:
            List of delivery reports
            
        Raises:
            BeemAuthenticationError: Invalid credentials
            BeemConnectionError: Network error
        """
        # Clean phone number
        cleaned = PhoneNumberValidator.clean(dest_addr)
        
        # Use delivery reports base URL
        original_base = self.http.base_url
        self.http.base_url = self.dlr_base_url
        
        try:
            response = self.http.request(
                'GET',
                'public/v1/delivery-reports',
                params={
                    'dest_addr': cleaned,
                    'request_id': request_id
                }
            )
            result = self._handle_response(response)
            return result
        finally:
            self.http.base_url = original_base