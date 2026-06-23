from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

call = client.calls.create(
    to="+16156451400",  # your verified phone number
    from_=os.getenv("TWILIO_PHONE_NUMBER"),
    url="http://demo.twilio.com/docs/voice.xml"
)

print(f"Call SID: {call.sid}")