#!/usr/bin/env python3
"""
Example: Send OTP using Beem Africa SDK
"""

from beem_africa_sdk import CompleteBeemClient

def main():
    client = CompleteBeemClient(
        api_key="your_sms_api_key_here",
        secret_key="your_sms_secret_key_here",
        otp_api_key="dd3c361149334222",  # Your OTP API key
        otp_secret_key="NzFlMDc0YzkwNDgwZmY5YzBmZWI2MGQ3Y2YyN2ZkNTk4ZTUwYmRlNmZjZjM4MjAzOWE1MTAyMzViODEyNGE3Mw=="  # Your OTP secret key
    )

    try:
        # Configure approved sender IDs (used by default for OTP)
        client.set_approved_senders(["NanoBill"])
        print("✅ Configured approved sender IDs: NanoBill")

        # Send OTP with default settings (uses approved sender)
        print("📱 Sending OTP with default settings...")
        otp_data = client.send_otp("255755660639")
        pin_id = otp_data['pinId']
        print(f"✅ OTP sent! Pin ID: {pin_id}")

        # Send OTP with custom app ID and sender ID (NanoBill example)
        print("\n📱 Sending OTP with NanoBill branding...")
        otp_data = client.send_otp(
            phone="255755660639",
            app_id="4147",  # NanoBill app ID
            sender_id="NanoBill"  # Sender ID
        )
        pin_id = otp_data['pinId']
        print(f"✅ OTP sent from NanoBill! Pin ID: {pin_id}")

        # In a real application, you would get the code from user input
        # For demo purposes, we'll simulate user input
        user_code = input("Enter OTP code: ")

        # Verify OTP
        is_valid = client.verify_otp(pin_id, user_code)

        if is_valid:
            print("✅ OTP verified successfully!")
        else:
            print("❌ Invalid OTP code")

    except Exception as e:
        print(f"❌ OTP operation failed: {e}")

    client.close()

if __name__ == "__main__":
    main()