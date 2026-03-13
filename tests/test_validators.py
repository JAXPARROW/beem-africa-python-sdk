"""
Tests for phone number validation utilities.
"""

import pytest
from beem_africa_sdk.utils.validators import PhoneNumberValidator


class TestPhoneNumberValidator:
    """Test phone number validation functionality."""

    def test_validate_valid_numbers(self):
        """Test validation of valid Tanzanian numbers."""
        valid_numbers = [
            "255755660639",
            "0755660639",  # Local format
            "+255755660639",  # International with +
            "255 755 660 639",  # With spaces
            "255-755-660-639",  # With dashes
        ]

        for number in valid_numbers:
            assert PhoneNumberValidator.validate(number), f"Failed to validate: {number}"

    def test_validate_invalid_numbers(self):
        """Test validation of invalid numbers."""
        invalid_numbers = [
            "123456789",  # Too short
            "255755660639123",  # Too long
            "25575566063",  # Wrong length
            "155755660639",  # Wrong country code
            "",  # Empty
            "abc",  # Non-numeric
        ]

        for number in invalid_numbers:
            assert not PhoneNumberValidator.validate(number), f"Incorrectly validated: {number}"

    def test_clean_valid_numbers(self):
        """Test cleaning of valid numbers."""
        test_cases = [
            ("0755660639", "255755660639"),
            ("255755660639", "255755660639"),
            ("+255755660639", "255755660639"),
            ("255 755 660 639", "255755660639"),
            ("255-755-660-639", "255755660639"),
        ]

        for input_num, expected in test_cases:
            result = PhoneNumberValidator.clean(input_num)
            assert result == expected, f"Clean failed: {input_num} -> {result}, expected {expected}"

    def test_clean_invalid_numbers(self):
        """Test cleaning of invalid numbers raises ValueError."""
        invalid_numbers = [
            "123456789",
            "",
            "abc",
        ]

        for number in invalid_numbers:
            with pytest.raises(ValueError):
                PhoneNumberValidator.clean(number)

    def test_validate_batch(self):
        """Test batch validation."""
        numbers = ["255755660639", "0755660639", "invalid"]
        results = PhoneNumberValidator.validate_batch(numbers)

        expected = [
            ("255755660639", True),
            ("0755660639", True),
            ("invalid", False),
        ]

        assert results == expected

    def test_clean_batch(self):
        """Test batch cleaning."""
        numbers = ["0755660639", "255712345678"]
        results = PhoneNumberValidator.clean_batch(numbers)

        expected = ["255755660639", "255712345678"]
        assert results == expected

    def test_clean_batch_with_invalid(self):
        """Test batch cleaning with invalid numbers raises ValueError."""
        numbers = ["0755660639", "invalid"]

        with pytest.raises(ValueError):
            PhoneNumberValidator.clean_batch(numbers)