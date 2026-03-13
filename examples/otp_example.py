#!/usr/bin/env python3
"""
Example: Verifying One Time Password with Beem Africa

Apart from just sending SMS, Beem also provides OTP Services for One Time password
verification system that is expected to be expired after a certain time that has been specified.

You can also use OTP to do 2-factor-authentication system to your app/website,
Beem will generate a random OTP for you and provide you an endpoint to verify it.

This example shows how to send and verify OTP with Beem Africa SDK.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from beem_africa_sdk import OTP

def main():
    """Demonstrate OTP functionality with Beem Africa."""

    # Initialize OTP client with your credentials
    # Note: Using separate OTP credentials as provided
    otp_client = OTP(
        api_key="dd3c361149334222",  # SMS API key (can be same or different)
        secret_key="NzFlMDc0YzkwNDgwZmY5YzBmZWI2MGQ3Y2YyN2ZkNTk4ZTUwYmRlNmZjZjM4MjAzOWE1MTAyMzViODEyNGE3Mw==",  # SMS secret
        otp_api_key="dd3c361149334222",  # OTP API key
        otp_secret_key="NzFlMDc0YzkwNDgwZmY5YzBmZWI2MGQ3Y2YyN2ZkNTk4ZTUwYmRlNmZjZjM4MjAzOWE1MTAyMzViODEyNGE3Mw=="  # OTP secret
    )

    print("Beem Africa OTP Example")
    print("=" * 30)

    # Example 1: Send OTP
    print("\n1. Sending OTP...")
    try:
        # Replace with actual phone number for real testing
        # phone_number = "255755660639"  # Valid Tanzanian number format
        phone_number = "255712345678"  # Example valid number (for demo)
        app_id = "4147"  # NanoBill app ID

        print(f"Sending OTP to: {phone_number}")
        print("(Note: Replace with real phone number for actual testing)")

        result = otp_client.send_otp(phone_number, app_id=app_id)
        print(f"Result: {result}")

        # Expected result format:
        # {'data': {'pinId': '4a5c2141-c965-4a9d-aca4-54f58063e831',
        #           'message': {'code': 100, 'message': 'SMS sent successfully'}}}

        if 'data' in result and 'pinId' in result['data']:
            pin_id = result['data']['pinId']
            print(f"✓ OTP sent! Pin ID: {pin_id}")

            # Example 2: Verify OTP
            print("\n2. Verifying OTP...")
            print("Note: In real usage, get the PIN from user input")
            print("For this demo, we'll show the API call structure:")

            # This is what you would do in real code:
            # pin_from_user = input("Enter the PIN you received: ")
            # verification_result = otp_client.verify_otp(pin_id, pin_from_user)

            print(f"otp_client.verify_otp(pin_id='{pin_id}', pin='122496')")

            # Expected successful verification result:
            # {'data': {'message': {'code': 117, 'message': 'Valid Pin'}}}

            print("\nExpected successful result:")
            print("{'data': {'message': {'code': 117, 'message': 'Valid Pin'}}}")

            # Test with invalid PIN (for demonstration)
            print("\n3. Testing invalid PIN (should return False)...")
            try:
                invalid_result = otp_client.verify_otp(pin_id, "000000")
                print(f"Invalid PIN result: {invalid_result}")
            except Exception as e:
                print(f"Error (expected): {e}")

        else:
            print("❌ Failed to send OTP - check credentials and phone number")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: OTP service may not be enabled on your Beem account.")
        print("Contact Beem support to enable OTP functionality.")

    finally:
        # Always close the client
        otp_client.close()

if __name__ == "__main__":
    main()