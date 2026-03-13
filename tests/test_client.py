"""
Tests for Beem client functionality.
"""

import pytest
from unittest.mock import Mock, patch
from beem_africa_sdk import CompleteBeemClient
from beem_africa_sdk.exceptions import BeemAuthenticationError, BeemAPIError


class TestBeemClient:
    """Test Beem client functionality."""

    def test_client_initialization(self):
        """Test client initializes correctly."""
        with patch('beem_africa_sdk.client.PooledHTTPClient') as mock_http:
            mock_instance = Mock()
            mock_http.return_value = mock_instance

            client = CompleteBeemClient(
                api_key="test_key",
                secret_key="test_secret",
                timeout=60,
                max_retries=5
            )

            mock_http.assert_called_once_with(
                api_key="test_key",
                secret_key="test_secret",
                base_url="https://apisms.beem.africa",
                timeout=60,
                max_retries=5,
                pool_connections=10,
                pool_maxsize=100,
                logger=None
            )

    def test_context_manager(self):
        """Test client works as context manager."""
        with patch('beem_africa_sdk.client.PooledHTTPClient') as mock_http:
            mock_instance = Mock()
            mock_http.return_value = mock_instance

            with CompleteBeemClient("key", "secret") as client:
                assert client is not None

            mock_instance.close.assert_called_once()

    def test_is_healthy_success(self, mock_client):
        """Test health check returns True on success."""
        client, mock_http = mock_client

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http.request.return_value = mock_response
        mock_http.base_url = "https://apisms.beem.africa"

        # Mock _handle_response to avoid JSON parsing
        client._handle_response = Mock(return_value={'data': {'credit_balance': '100'}})

        assert client.is_healthy() is True
        mock_http.request.assert_called_once()

    def test_is_healthy_failure(self, mock_client):
        """Test health check returns False on failure."""
        client, mock_http = mock_client

        mock_http.request.side_effect = Exception("Connection failed")

        assert client.is_healthy() is False

    def test_handle_response_success(self, mock_client):
        """Test successful response handling."""
        client, mock_http = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        # Remove our mock to test the real method
        del client._handle_response

        result = client._handle_response(mock_response, 200)
        assert result == {"success": True}

    def test_handle_response_auth_error(self, mock_client):
        """Test authentication error handling."""
        client, mock_http = mock_client

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        del client._handle_response

        with pytest.raises(BeemAuthenticationError):
            client._handle_response(mock_response)

    def test_handle_response_api_error(self, mock_client):
        """Test API error handling."""
        client, mock_http = mock_client

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"code": 111, "message": "Invalid sender"}

        del client._handle_response

        with pytest.raises(BeemAPIError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.code == 111