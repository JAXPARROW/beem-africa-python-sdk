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

# Initialize with your API credentials
client = CompleteBeemClient(
    api_key="your_api_key",
    secret_key="your_secret_key"
)

# Check API health
if client.is_healthy():
    print("✅ Beem API is accessible")
else:
    print("❌ Beem API is unreachable")
```

### Send SMS

```python
# Send SMS to single recipient
response = client.send_sms(
    source_addr="NANOBILL",
    message="Your voucher code: ABC123XYZ",
    recipients="255755660639"
)

print(f"✅ SMS sent! Request ID: {response['request_id']}")

# Send SMS to multiple recipients
response = client.send_sms(
    source_addr="COMPANY",
    message="Hello valued customers!",
    recipients=["255755660639", "255712345678", "255798765432"]
)

print(f"Valid: {response['valid']}, Invalid: {response['invalid']}")
```

### Send OTP

```python
# Send OTP
otp_data = client.send_otp("255755660639")
pin_id = otp_data['pinId']
print(f"📱 OTP sent! Pin ID: {pin_id}")

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