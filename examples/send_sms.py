#!/usr/bin/env python3
"""
Example: Send SMS using Beem Africa SDK
"""

from beem_africa_sdk import CompleteBeemClient

def main():
    # Initialize client
    client = CompleteBeemClient(
        api_key="your_api_key_here",
        secret_key="your_secret_key_here"
    )

    # Check health
    if client.is_healthy():
        print("✅ Beem API is healthy")
    else:
        print("❌ Beem API is unreachable")
        return

    try:
        # Send SMS to single recipient
        response = client.send_sms(
            source_addr="NANOBILL",
            message="Your voucher code: ABC123XYZ",
            recipients="255755660639"
        )
        print(f"✅ SMS sent! Request ID: {response['request_id']}")
        print(f"Valid: {response['valid']}, Invalid: {response['invalid']}")

    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")

    # Close client
    client.close()

if __name__ == "__main__":
    main()