from flask import Flask, Response
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)


@app.route("/voice", methods=["GET", "POST"])
def voice():
    response = VoiceResponse()
    response.say(
        "Hello, this is Athena. I would like to schedule an appointment.",
        voice="alice",
        language="en-US"
    )
    response.pause(length=1)
    response.say("Thank you. Goodbye.", voice="alice", language="en-US")
    response.hangup()

    return Response(str(response), mimetype="text/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
