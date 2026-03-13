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
        # Configure approved sender IDs
        client.set_approved_senders(["NANOBILL", "COMPANY"])
        print("✅ Configured approved sender IDs: NANOBILL, COMPANY")

        # Send SMS using default approved sender (NANOBILL)
        response = client.send_sms(
            message="Your voucher code: ABC123XYZ",
            recipients="255755660639"
        )
        print(f"✅ SMS sent with default sender! Request ID: {response['request_id']}")

        # Send SMS with specific sender
        response = client.send_sms(
            message="Hello from COMPANY!",
            recipients="255755660639",
            source_addr="COMPANY"
        )
        print(f"✅ SMS sent with COMPANY sender! Request ID: {response['request_id']}")
        print(f"Valid: {response['valid']}, Invalid: {response['invalid']}")

    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")

    # Close client
    client.close()

if __name__ == "__main__":
    main()