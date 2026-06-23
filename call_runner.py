

import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TEST_TO_PHONE_NUMBER = os.getenv("TEST_TO_PHONE_NUMBER")
VOICE_WEBHOOK_URL = os.getenv("VOICE_WEBHOOK_URL")


def validate_environment():
    missing_values = []

    if not TWILIO_ACCOUNT_SID:
        missing_values.append("TWILIO_ACCOUNT_SID")

    if not TWILIO_AUTH_TOKEN:
        missing_values.append("TWILIO_AUTH_TOKEN")

    if not TWILIO_PHONE_NUMBER:
        missing_values.append("TWILIO_PHONE_NUMBER")

    if not TEST_TO_PHONE_NUMBER:
        missing_values.append("TEST_TO_PHONE_NUMBER")

    if not VOICE_WEBHOOK_URL:
        missing_values.append("VOICE_WEBHOOK_URL")

    if missing_values:
        missing_text = ", ".join(missing_values)
        raise ValueError(f"Missing required environment variables: {missing_text}")


def make_test_call():
    validate_environment()

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    call = client.calls.create(
        to=TEST_TO_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        url=VOICE_WEBHOOK_URL,
        record=True,
    )

    print("Test call started successfully.")
    print(f"Call SID: {call.sid}")
    print(f"From: {TWILIO_PHONE_NUMBER}")
    print(f"To: {TEST_TO_PHONE_NUMBER}")
    print(f"Webhook: {VOICE_WEBHOOK_URL}")


if __name__ == "__main__":
    make_test_call()