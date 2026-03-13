#!/usr/bin/env python3
"""
Example: Health check using Beem Africa SDK
"""

from beem_africa_sdk import CompleteBeemClient

def main():
    client = CompleteBeemClient(
        api_key="your_api_key_here",
        secret_key="your_secret_key_here"
    )

    # Check API health
    if client.is_healthy():
        print("✅ Beem API is healthy and accessible")
        print("✅ Credentials are valid")

        # Get balance as additional health check
        try:
            balance = client.get_balance()
            print(f"✅ SMS Balance: {balance} credits")
        except Exception as e:
            print(f"⚠️  Could not retrieve balance: {e}")

    else:
        print("❌ Beem API is unreachable or credentials are invalid")
        print("❌ Please check your API key, secret key, and internet connection")

    client.close()

if __name__ == "__main__":
    main()