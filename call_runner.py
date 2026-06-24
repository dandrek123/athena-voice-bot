import argparse
import os
from urllib.parse import urlencode

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TEST_TO_PHONE_NUMBER = os.getenv("TEST_TO_PHONE_NUMBER")
VOICE_WEBHOOK_URL = os.getenv("VOICE_WEBHOOK_URL")

SCENARIOS = {
    "appointment": "new_patient.txt",
    "refill": "refill_patient.txt",
    "insurance": "insurance_patient.txt",
    "cancel": "cancel_patient.txt",
    "reschedule": "reschedule_patient.txt",
    "registration": "new_registration_patient.txt",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Start an Athena voice bot test call.")
    parser.add_argument(
        "--scenario",
        choices=SCENARIOS.keys(),
        default="appointment",
        help="Voice scenario to run. Defaults to appointment.",
    )
    return parser.parse_args()


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


def build_voice_url(scenario):
    scenario_file = SCENARIOS[scenario]
    query_string = urlencode({"scenario": scenario_file})
    return f"{VOICE_WEBHOOK_URL}?{query_string}"


def make_test_call(scenario):
    validate_environment()

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    voice_url = build_voice_url(scenario)

    call = client.calls.create(
        to=TEST_TO_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        url=voice_url,
        record=True,
    )

    print("Test call started successfully.")
    print(f"Scenario: {scenario}")
    print(f"Call SID: {call.sid}")
    print(f"From: {TWILIO_PHONE_NUMBER}")
    print(f"To: {TEST_TO_PHONE_NUMBER}")
    print(f"Webhook: {voice_url}")


if __name__ == "__main__":
    args = parse_args()
    make_test_call(args.scenario)