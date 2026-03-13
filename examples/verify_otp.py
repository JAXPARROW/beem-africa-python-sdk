#!/usr/bin/env python3
"""
Example: Verify OTP using Beem Africa SDK
"""

from beem_africa_sdk import CompleteBeemClient

def main():
    client = CompleteBeemClient(
        api_key="your_api_key_here",
        secret_key="your_secret_key_here"
    )

    # In a real scenario, pin_id would come from send_otp response
    pin_id = "your_pin_id_here"  # Replace with actual pin_id
    user_code = input("Enter OTP code: ")

    try:
        is_valid = client.verify_otp(pin_id, user_code)

        if is_valid:
            print("✅ OTP verified successfully!")
        else:
            print("❌ Invalid OTP code")

    except Exception as e:
        print(f"❌ OTP verification failed: {e}")

    client.close()

if __name__ == "__main__":
    main()