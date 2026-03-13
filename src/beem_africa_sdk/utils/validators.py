"""
Phone number validation utilities for Tanzanian numbers.
"""

import re
from typing import Union, List, Tuple


class PhoneNumberValidator:
    """Validator for Tanzanian phone numbers (format: 255XXXXXXXXX)"""
    
    # Tanzania country code
    COUNTRY_CODE = "255"
    VALID_LENGTH = 12  # 255 + 9 digits
    
    @classmethod
    def validate(cls, phone: str) -> bool:
        """
        Validate a single phone number.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not phone or not isinstance(phone, str):
            return False
        
        # Remove any non-digit characters
        cleaned = re.sub(r'\D', '', phone)
        
        # Check if it's a valid Tanzanian number
        if cleaned.startswith('0'):
            cleaned = cls.COUNTRY_CODE + cleaned[1:]
        
        return (
            len(cleaned) == cls.VALID_LENGTH and
            cleaned.startswith(cls.COUNTRY_CODE) and
            cleaned.isdigit()
        )
    
    @classmethod
    def clean(cls, phone: str) -> str:
        """
        Clean and format a phone number to standard format (255XXXXXXXXX).
        
        Args:
            phone: Phone number to clean
            
        Returns:
            Cleaned phone number
            
        Raises:
            ValueError: If phone number is invalid
        """
        if not phone:
            raise ValueError("Phone number cannot be empty")
        
        # Remove all non-digit characters
        cleaned = re.sub(r'\D', '', phone)
        
        # Convert from local format (0XXXXXXXXX) to international
        if cleaned.startswith('0'):
            cleaned = cls.COUNTRY_CODE + cleaned[1:]
        
        # Validate
        if not cls.validate(cleaned):
            raise ValueError(
                f"Invalid Tanzanian phone number: {phone}. "
                f"Expected format: {cls.COUNTRY_CODE}XXXXXXXXX (12 digits)"
            )
        
        return cleaned
    
    @classmethod
    def validate_batch(cls, phones: List[str]) -> List[Tuple[str, bool]]:
        """
        Validate multiple phone numbers.
        
        Args:
            phones: List of phone numbers
            
        Returns:
            List of tuples (phone, is_valid)
        """
        return [(phone, cls.validate(phone)) for phone in phones]
    
    @classmethod
    def clean_batch(cls, phones: List[str]) -> List[str]:
        """
        Clean multiple phone numbers.
        
        Args:
            phones: List of phone numbers
            
        Returns:
            List of cleaned phone numbers
            
        Raises:
            ValueError: If any phone number is invalid
        """
        return [cls.clean(phone) for phone in phones]