#!/usr/bin/env python3
"""
Example: Send OTP using Beem Africa SDK
"""

from beem_africa_sdk import CompleteBeemClient

def main():
    client = CompleteBeemClient(
        api_key="your_sms_api_key_here",
        secret_key="your_sms_secret_key_here",
        otp_api_key="your_otp_api_key_here",  # Your OTP API key
        otp_secret_key="your_otp_secret_key_here"  # Your OTP secret key
    )

    try:
        # Configure approved sender IDs (used by default for OTP)
        client.set_approved_senders(["INFO"])
        print("✅ Configured approved sender IDs: INFO")

        # Send OTP with default settings (uses approved sender)
        print("📱 Sending OTP with default settings...")
        otp_data = client.send_otp("255712345678")
        pin_id = otp_data['pinId']
        print(f"✅ OTP sent! Pin ID: {pin_id}")

        # Send OTP with custom app ID and sender ID
        print("\n📱 Sending OTP with custom app ID...")
        otp_data = client.send_otp(
            phone="255712345678",
            app_id="your_app_id",
            sender_id="INFO"
        )
        pin_id = otp_data['pinId']
        print(f"✅ OTP sent! Pin ID: {pin_id}")

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