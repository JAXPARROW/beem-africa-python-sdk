#!/usr/bin/env python3
"""
Example: Schedule SMS using Beem Africa SDK

The schedule_time parameter accepts UTC time in "yyyy-mm-dd hh:mm" format.
Beem will deliver the message at the specified time.
"""

from datetime import datetime, timezone, timedelta
from beem_africa_sdk import CompleteBeemClient


def main():
    client = CompleteBeemClient(
        api_key="your_api_key_here",
        secret_key="your_secret_key_here"
    )

    client.set_approved_senders(["INFO"])

    # Schedule time: 2 hours from now (UTC)
    send_at = datetime.now(timezone.utc) + timedelta(hours=2)
    schedule_time = send_at.strftime("%Y-%m-%d %H:%M")
    print(f"Scheduling SMS for: {schedule_time} UTC")

    try:
        # --- Single recipient ---
        response = client.send_sms(
            message="Hello! This is a scheduled message.",
            recipients="255712345678",
            source_addr="INFO",
            schedule_time=schedule_time
        )
        print(f"Scheduled (single): request_id={response['request_id']}")
        print(f"  Valid: {response['valid']}, Invalid: {response['invalid']}")

        # --- Multiple recipients ---
        response = client.send_sms(
            message="Hello team! This is a scheduled broadcast.",
            recipients=[
                "255712345678",
                "255798765432",
                "255754321098"
            ],
            source_addr="INFO",
            schedule_time=schedule_time
        )
        print(f"Scheduled (bulk):   request_id={response['request_id']}")
        print(f"  Valid: {response['valid']}, Invalid: {response['invalid']}")

    except Exception as e:
        print(f"Failed to schedule SMS: {e}")

    client.close()


if __name__ == "__main__":
    main()
