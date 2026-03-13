"""
Tests for SMS functionality.
"""

import pytest
from unittest.mock import Mock
from beem_africa_sdk.exceptions import BeemValidationError


class TestSMSMixin:
    """Test SMS functionality."""

    def test_send_sms_single_recipient(self, mock_client, sample_sms_response):
        """Test sending SMS to single recipient."""
        client, mock_http = mock_client

        client._handle_response.return_value = sample_sms_response

        result = client.send_sms(
            source_addr="TEST",
            message="Hello world",
            recipients="255755660639"
        )

        assert result == sample_sms_response
        mock_http.request.assert_called_once()

        # Check request payload
        call_args = mock_http.request.call_args
        payload = call_args[1]['json']  # kwargs

        assert payload['source_addr'] == "TEST"
        assert payload['message'] == "Hello world"
        assert len(payload['recipients']) == 1
        assert payload['recipients'][0]['dest_addr'] == "255755660639"

    def test_send_sms_multiple_recipients(self, mock_client, sample_sms_response):
        """Test sending SMS to multiple recipients."""
        client, mock_http = mock_client

        client._handle_response.return_value = sample_sms_response

        recipients = ["255755660639", "255712345678"]
        result = client.send_sms(
            source_addr="TEST",
            message="Hello world",
            recipients=recipients
        )

        assert result == sample_sms_response

        # Check request payload
        call_args = mock_http.request.call_args
        payload = call_args[1]['json']

        assert len(payload['recipients']) == 2
        assert payload['recipients'][0]['dest_addr'] == "255755660639"
        assert payload['recipients'][1]['dest_addr'] == "255712345678"

    def test_send_sms_invalid_sender(self, mock_client):
        """Test sending SMS with invalid sender ID."""
        client, mock_http = mock_client

        with pytest.raises(BeemValidationError):
            client.send_sms(
                source_addr="",  # Empty sender
                message="Hello",
                recipients="255755660639"
            )

    def test_send_sms_invalid_recipients(self, mock_client):
        """Test sending SMS with invalid recipients."""
        client, mock_http = mock_client

        with pytest.raises(BeemValidationError):
            client.send_sms(
                source_addr="TEST",
                message="Hello",
                recipients=[]  # Empty list
            )

    def test_send_sms_invalid_phone(self, mock_client):
        """Test sending SMS with invalid phone number."""
        client, mock_http = mock_client

        with pytest.raises(BeemValidationError):
            client.send_sms(
                source_addr="TEST",
                message="Hello",
                recipients="invalid_phone"
            )

    def test_get_balance(self, mock_client, sample_balance_response):
        """Test getting SMS balance."""
        client, mock_http = mock_client

        client._handle_response.return_value = sample_balance_response

        result = client.get_balance()

        assert result == 100.50
        mock_http.request.assert_called_once_with('GET', 'public/v1/vendors/balance')

    def test_get_delivery_report(self, mock_client):
        """Test getting delivery report."""
        client, mock_http = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_http.request.return_value = mock_response
        client._handle_response.return_value = [{"status": "DELIVERED"}]

        result = client.get_delivery_report(
            dest_addr="255755660639",
            request_id="12345"
        )

        assert result == [{"status": "DELIVERED"}]

        # Verify the request was made with correct parameters
        mock_http.request.assert_called_with(
            'GET',
            'public/v1/delivery-reports',
            params={
                'dest_addr': '255755660639',
                'request_id': '12345'
            }
        )