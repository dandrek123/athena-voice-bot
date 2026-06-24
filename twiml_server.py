import os
from datetime import datetime

from flask import Flask, Response, request
from twilio.twiml.voice_response import Gather, VoiceResponse

app = Flask(__name__)

os.makedirs("transcripts", exist_ok=True)

TRANSCRIPT_FILE = datetime.now().strftime("transcripts/voice_call_%Y%m%d_%H%M%S.txt")


def save_turn(role, message):
    with open(TRANSCRIPT_FILE, "a") as file:
        file.write(f"{role}: {message}\n")


def twiml_response(response):
    return Response(str(response), mimetype="text/xml")


@app.route("/voice", methods=["GET", "POST"])
def voice():
    response = VoiceResponse()

    opening_message = "Hello, this is Athena. I would like to schedule an appointment."
    save_turn("Athena", opening_message)

    gather = Gather(
        input="speech",
        action="/process_speech",
        method="POST",
        speech_timeout="auto",
        timeout=5,
    )

    gather.say(opening_message, voice="alice", language="en-US")
    response.append(gather)

    response.say(
        "I did not hear a response. Thank you. Goodbye.",
        voice="alice",
        language="en-US",
    )
    response.hangup()

    return twiml_response(response)


@app.route("/process_speech", methods=["GET", "POST"])
def process_speech():
    response = VoiceResponse()

    speech_result = request.form.get("SpeechResult", "").strip()
    save_turn("Agent", speech_result if speech_result else "[No speech detected]")

    speech_text = speech_result.lower()

    if not speech_result:
        reply = "I am sorry, I did not catch that. Could you repeat that?"
    elif "name" in speech_text:
        reply = "My name is Sarah Johnson."
    elif "birth" in speech_text or "date of birth" in speech_text:
        reply = "My date of birth is January tenth, nineteen ninety two."
    elif "insurance" in speech_text:
        reply = "I have Blue Cross Blue Shield insurance."
    elif "date" in speech_text or "day" in speech_text or "time" in speech_text:
        reply = "Next Tuesday morning would work for me if you have availability."
    else:
        reply = "Yes, I can provide that information. What do you need from me?"

    save_turn("Athena", reply)

    gather = Gather(
        input="speech",
        action="/process_speech",
        method="POST",
        speech_timeout="auto",
        timeout=5,
    )

    gather.say(reply, voice="alice", language="en-US")
    response.append(gather)

    response.pause(length=1)
    response.redirect("/process_speech", method="POST")

    return twiml_response(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
