"""
Custom exception hierarchy for Beem Africa SDK.
All exceptions inherit from BeemError for easy catching.
"""

class BeemError(Exception):
    """Base exception for all Beem SDK errors"""
    pass


class BeemAuthenticationError(BeemError):
    """Invalid API credentials (HTTP 401)"""
    pass


class BeemValidationError(BeemError):
    """Input validation failed (e.g., invalid phone number)"""
    pass


class BeemAPIError(BeemError):
    """API returned an error response"""
    def __init__(self, message: str, code: int = None, response_data: dict = None):
        super().__init__(message)
        self.code = code
        self.response_data = response_data or {}


class BeemRateLimitError(BeemAPIError):
    """Rate limit exceeded (HTTP 429)"""
    pass


class BeemInsufficientBalanceError(BeemAPIError):
    """Not enough credit to send SMS"""
    pass


class BeemInvalidSenderError(BeemAPIError):
    """Sender ID not approved or invalid"""
    pass


class BeemConnectionError(BeemError):
    """Network-level error (timeout, DNS failure)"""
    pass


class BeemServerError(BeemAPIError):
    """Beem server error (HTTP 5xx)"""
    pass