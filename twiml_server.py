import os
from datetime import datetime

from flask import Flask, Response, request
from twilio.twiml.voice_response import Gather, VoiceResponse
from patient import load_persona, patient_response

app = Flask(__name__)

os.makedirs("transcripts", exist_ok=True)

TRANSCRIPT_FILE = datetime.now().strftime("transcripts/voice_call_%Y%m%d_%H%M%S.txt")
NO_SPEECH_COUNT = 0

VOICE_SCENARIO_FILE = os.getenv("VOICE_SCENARIO_FILE", "new_patient.txt")
load_persona(VOICE_SCENARIO_FILE)


def get_opening_message():
    scenario_name = VOICE_SCENARIO_FILE.lower()

    if "refill" in scenario_name:
        return "Hello, this is Athena. I need a refill for my prescription."

    if "insurance" in scenario_name:
        return "Hello, this is Athena. I need to update my insurance information."

    if "cancel" in scenario_name:
        return "Hello, this is Athena. I would like to cancel my appointment."

    if "reschedule" in scenario_name:
        return "Hello, this is Athena. I would like to reschedule my appointment."

    return "Hello, this is Athena. I would like to schedule an appointment."


def save_turn(role, message):
    with open(TRANSCRIPT_FILE, "a") as file:
        file.write(f"{role}: {message}\n")


def twiml_response(response):
    return Response(str(response), mimetype="text/xml")


@app.route("/voice", methods=["GET", "POST"])
def voice():
    response = VoiceResponse()

    opening_message = get_opening_message()
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
    global NO_SPEECH_COUNT

    speech_result = request.form.get("SpeechResult", "").strip()
    save_turn("Agent", speech_result if speech_result else "[No speech detected]")

    speech_text = speech_result.lower()

    if not speech_result:
        NO_SPEECH_COUNT += 1

        if NO_SPEECH_COUNT == 1:
            reply = "I am sorry, I did not catch that. Could you repeat that?"
        elif NO_SPEECH_COUNT == 2:
            reply = "I still cannot hear you clearly. Could you say that one more time?"
        else:
            closing_message = "I still cannot hear a response. Thank you for your time. Goodbye."
            save_turn("Athena", closing_message)
            response.say(closing_message, voice="alice", language="en-US")
            response.hangup()
            return twiml_response(response)

    else:
        NO_SPEECH_COUNT = 0

        if "thank you" in speech_text or "thanks" in speech_text or "goodbye" in speech_text or "bye" in speech_text:
            closing_message = "You're welcome. Thank you for your time. Goodbye."
            save_turn("Athena", closing_message)
            response.say(closing_message, voice="alice", language="en-US")
            response.hangup()
            return twiml_response(response)

        reply = patient_response(speech_result)

    save_turn("Athena", reply)

    reply_text = reply.lower()
    should_end_call = (
        "that is all" in reply_text
        or "nothing else" in reply_text
        or "thank you" in reply_text
        or "goodbye" in reply_text
        or "bye" in reply_text
    )

    if should_end_call:
        response.say(reply, voice="alice", language="en-US")
        response.hangup()
        return twiml_response(response)

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
