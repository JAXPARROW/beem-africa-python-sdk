"""
Beem Africa Python SDK - Enterprise-ready SDK for Beem Africa APIs.

Focus features: SMS and OTP
"""

from .client import BeemClient
from .sms import SMSMixin
from .otp import OTPMixin
from .exceptions import (
    BeemError,
    BeemAuthenticationError,
    BeemValidationError,
    BeemAPIError,
    BeemRateLimitError,
    BeemInsufficientBalanceError,
    BeemInvalidSenderError,
    BeemConnectionError,
    BeemServerError
)

# Apply mixins to BeemClient
class CompleteBeemClient(BeemClient, SMSMixin, OTPMixin):
    """Complete Beem client with all features"""
    pass

# For backward compatibility with original library
Authorize = CompleteBeemClient
SMS = CompleteBeemClient
OTP = CompleteBeemClient

__all__ = [
    'CompleteBeemClient',
    'Authorize',
    'SMS',
    'OTP',
    'BeemError',
    'BeemAuthenticationError',
    'BeemValidationError',
    'BeemAPIError',
    'BeemRateLimitError',
    'BeemInsufficientBalanceError',
    'BeemInvalidSenderError',
    'BeemConnectionError',
    'BeemServerError',
]

__version__ = '0.2.0'