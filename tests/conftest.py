"""
Pytest configuration and fixtures for Beem Africa SDK tests.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from beem_africa_sdk import CompleteBeemClient


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    with patch('beem_africa_sdk.client.PooledHTTPClient') as mock_http:
        mock_instance = Mock()
        mock_http.return_value = mock_instance

        client = CompleteBeemClient(
            api_key="test_key",
            secret_key="test_secret"
        )

        # Mock the _handle_response method
        client._handle_response = Mock()

        return client, mock_instance


@pytest.fixture
def sample_sms_response():
    """Sample SMS send response."""
    return {
        'request_id': '12345',
        'valid': 1,
        'invalid': 0,
        'successful': True,
        'code': 100,
        'message': 'Message Submitted Successfully'
    }


@pytest.fixture
def sample_otp_response():
    """Sample OTP send response."""
    return {
        'data': {
            'pinId': 'test-pin-id-123',
            'message': {
                'code': 100,
                'message': 'SMS sent successfully'
            }
        }
    }


@pytest.fixture
def sample_balance_response():
    """Sample balance response."""
    return {
        'data': {
            'credit_balance': '100.50'
        }
    }