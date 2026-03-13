# Beem Africa Python SDK

Enterprise-ready Python SDK for Beem Africa APIs with focus on SMS and OTP functionality.

[![PyPI version](https://badge.fury.io/py/beem-africa-python-sdk.svg)](https://pypi.org/project/beem-africa-python-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/beem-africa-python-sdk)](https://pypi.org/project/beem-africa-python-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- ✅ **Connection Pooling** - Reuse connections for better performance
- ✅ **Health Check** - `is_healthy()` method for monitoring
- ✅ **Exponential Backoff** - Automatic retry with smart backoff
- ✅ **Comprehensive Error Handling** - Detailed exception hierarchy
- ✅ **Full Type Hints** - Complete mypy compliance
- ✅ **Configurable Logging** - Built-in logging support
- ✅ **Context Manager Support** - Use with `with` statements
- ✅ **Phone Number Validation** - Automatic Tanzanian number formatting

## Installation

```bash
pip install beem-africa-python-sdk
```

## Quick Start

### Initialize Client

```python
from beem_africa_sdk import CompleteBeemClient

# For separate SMS and OTP credentials (recommended)
client = CompleteBeemClient(
    api_key="your_sms_api_key",           # SMS API key
    secret_key="your_sms_secret_key",     # SMS secret key
    otp_api_key="your_otp_api_key_here",       # OTP API key (separate)
    otp_secret_key="your_otp_secret_key_here"  # OTP secret key (separate)
)

# For same credentials (if your account uses same keys for both)
client = CompleteBeemClient(
    api_key="your_api_key",
    secret_key="your_secret_key"
    # otp_api_key and otp_secret_key will default to api_key/secret_key
)

# Check API health
if client.is_healthy():
    print("✅ Beem API is accessible")
else:
    print("❌ Beem API is unreachable")
```

### Manage Sender IDs

```python
# Set approved sender IDs for your account
client.set_approved_senders(["NANOBILL", "COMPANY", "ALERTS"])

# Add individual sender IDs
client.add_approved_sender("PROMO")

# Get list of approved senders
approved = client.get_approved_senders()
print(f"Approved senders: {approved}")

# Validate if a sender ID is approved (sends test SMS)
is_valid = client.validate_sender_id("NANOBILL")
print(f"NANOBILL is approved: {is_valid}")
```

### Send SMS

```python
# Configure approved sender IDs
client.set_approved_senders(["NANOBILL", "COMPANY"])

# Send SMS using default approved sender (NANOBILL)
response = client.send_sms(
    message="Your voucher code: ABC123XYZ",
    recipients="255755660639"
)

# Send SMS with specific sender
response = client.send_sms(
    message="Hello valued customers!",
    recipients=["255755660639", "255712345678", "255798765432"],
    source_addr="COMPANY"
)

print(f"Valid: {response['valid']}, Invalid: {response['invalid']}")
```

### Send OTP

**Note:** OTP functionality uses separate API credentials from SMS. Beem provides different API keys for SMS and OTP services. Use your OTP-specific credentials:

```python
# Send OTP with NanoBill app (using separate OTP credentials)
otp_data = client.send_otp("255755660639", app_id="4147")
pin_id = otp_data['data']['pinId']
print(f"📱 OTP sent! Pin ID: {pin_id}")

# Send OTP with custom sender ID
otp_data = client.send_otp(
    phone="255755660639",
    app_id="4147",  # Your NanoBill app ID
    sender_id="NanoBill"  # Your sender ID
)
pin_id = otp_data['data']['pinId']
print(f"📱 OTP sent from NanoBill! Pin ID: {pin_id}")

# Later, verify OTP (user enters code)
user_code = input("Enter OTP code: ")
is_valid = client.verify_otp(pin_id, user_code)

if is_valid:
    print("✅ OTP verified successfully!")
else:
    print("❌ Invalid OTP code")
```

### Get Balance & Delivery Reports

```python
# Check SMS balance
balance = client.get_balance()
print(f"Current balance: {balance} SMS credits")

# Get delivery report (call after 5+ minutes)
reports = client.get_delivery_report(
    dest_addr="255755660639",
    request_id="your_request_id"
)

for report in reports:
    print(f"Status: {report['status']}, Timestamp: {report['timestamp']}")
```

### Context Manager Usage

```python
# Automatic resource cleanup
with CompleteBeemClient("api_key", "secret_key") as client:
    client.send_sms("SENDER", "Hello!", ["255755660639"])
    # Client automatically closed here
```

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

```python
from beem_africa_sdk import CompleteBeemClient
from beem_africa_sdk.exceptions import (
    BeemAuthenticationError,
    BeemValidationError,
    BeemInsufficientBalanceError,
    BeemConnectionError
)

client = CompleteBeemClient("api_key", "secret_key")

try:
    client.send_sms("SENDER", "Hello!", ["invalid_phone"])
except BeemValidationError as e:
    print(f"Validation error: {e}")
except BeemAuthenticationError as e:
    print(f"Authentication failed: {e}")
except BeemInsufficientBalanceError as e:
    print(f"Insufficient balance: {e}")
except BeemConnectionError as e:
    print(f"Connection error: {e}")
```

## API Reference

### CompleteBeemClient

Main client class with all functionality.

#### Constructor

```python
CompleteBeemClient(
    api_key: str,
    secret_key: str,
    timeout: int = 30,
    max_retries: int = 3,
    pool_connections: int = 10,
    pool_maxsize: int = 100,
    logger: Optional[logging.Logger] = None
)
```

#### Methods

- `is_healthy() -> bool` - Check API accessibility
- `send_sms(...) -> Dict[str, Any]` - Send SMS messages
- `get_balance() -> float` - Get SMS credit balance
- `get_delivery_report(...) -> List[Dict]` - Get delivery status
- `send_otp(...) -> Dict[str, Any]` - Send OTP
- `verify_otp(...) -> bool` - Verify OTP code
- `close()` - Close HTTP connections

## Phone Number Format

The SDK automatically validates and formats Tanzanian phone numbers:

- **Input formats accepted**: `0755660639`, `255755660639`, `+255755660639`
- **Output format**: `255755660639` (12 digits, no spaces or special chars)

## Configuration

### Environment Variables

Set credentials via environment variables:

```bash
export BEEM_API_KEY="your_api_key"
export BEEM_SECRET_KEY="your_secret_key"
```

### Logging

Configure logging for debugging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

client = CompleteBeemClient("api_key", "secret_key")
# All HTTP requests will be logged
```

## API Limitations

### SMS Restrictions
- **Unicode Characters**: Beem API does not support Unicode characters, emojis, or special symbols in SMS messages. Messages containing these will be rejected with an error.
- **Plain Text Only**: Use ASCII characters only for reliable delivery.
- **Sender ID**: Maximum 11 characters, alphanumeric only. Must be pre-approved by Beem.

### OTP Service
- **Account Dependent**: OTP functionality requires separate activation in your Beem account.
- **Setup Required**: Visit Beem dashboard → OTP menu → API Setup to generate API keys and configure applications.
- **Application ID**: Each OTP request requires an `app_id` that corresponds to your Beem application.
- **Error Codes**: 
  - `100`: SMS sent successfully
  - `101`: Failed to send SMS
  - `117`: Valid PIN (verification successful)
  - `114`: Incorrect PIN
  - `115`: PIN timeout
  - `116`: Attempts exceeded

### Delivery Reports
- **Timing**: Delivery reports should be requested at least 5 minutes after sending SMS.
- **Separate Endpoint**: Uses different API endpoint (`dlrapi.beem.africa`) than main SMS API.

## Development

### Setup

```bash
git clone https://github.com/JAXPARROW/beem-africa-python-sdk.git
cd beem-africa-python-sdk
pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

### Building

```bash
python -m build
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- 📖 [Documentation](https://github.com/JAXPARROW/beem-africa-python-sdk)
- 🐛 [Issues](https://github.com/JAXPARROW/beem-africa-python-sdk/issues)
- 💬 [Discussions](https://github.com/JAXPARROW/beem-africa-python-sdk/discussions)