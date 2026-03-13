#!/usr/bin/env python3
"""
Example: Send OTP using Beem Africa SDK
"""

from beem_africa_sdk import CompleteBeemClient

def main():
    client = CompleteBeemClient(
        api_key="your_api_key_here",
        secret_key="your_secret_key_here"
    )

    try:
        # Send OTP
        otp_data = client.send_otp("255755660639")
        pin_id = otp_data['pinId']
        print(f"📱 OTP sent! Pin ID: {pin_id}")

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