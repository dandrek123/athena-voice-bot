import os
from datetime import datetime

from flask import Flask, Response, request
from twilio.twiml.voice_response import Gather, VoiceResponse
from patient import load_persona, patient_response

app = Flask(__name__)

os.makedirs("transcripts", exist_ok=True)
os.makedirs("reports", exist_ok=True)

TRANSCRIPT_FILE = datetime.now().strftime("transcripts/voice_call_%Y%m%d_%H%M%S.txt")
NO_SPEECH_COUNT = 0
CALL_START_TIME = datetime.now()
CALL_OUTCOME = "In Progress"

VOICE_SCENARIO_FILE = os.getenv("VOICE_SCENARIO_FILE", "new_patient.txt")


def set_voice_scenario(scenario_file):
    global VOICE_SCENARIO_FILE
    VOICE_SCENARIO_FILE = scenario_file
    load_persona(VOICE_SCENARIO_FILE)


set_voice_scenario(VOICE_SCENARIO_FILE)


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

    if "registration" in scenario_name or "new_registration" in scenario_name:
        return "Hello, this is Athena. I would like to register as a new patient."

    return "Hello, this is Athena. I would like to schedule an appointment."


def save_turn(role, message):
    with open(TRANSCRIPT_FILE, "a") as file:
        file.write(f"{role}: {message}\n")


def get_scenario_display_name():
    scenario_name = VOICE_SCENARIO_FILE.lower()

    if "refill" in scenario_name:
        return "Prescription Refill"
    if "insurance" in scenario_name:
        return "Insurance Update"
    if "cancel" in scenario_name:
        return "Appointment Cancellation"
    if "reschedule" in scenario_name:
        return "Appointment Rescheduling"
    if "registration" in scenario_name or "new_registration" in scenario_name:
        return "New Patient Registration"

    return "Appointment Scheduling"


def checkbox(condition, label):
    mark = "✓" if condition else "□"
    return f"{mark} {label}"


def analyze_collected_information(transcript):
    transcript_text = transcript.lower()

    checks = [
        ("Patient name", "name" in transcript_text or "sarah johnson" in transcript_text),
        ("Date of birth", "date of birth" in transcript_text or "birth" in transcript_text),
        ("Insurance information", "insurance" in transcript_text or "blue cross" in transcript_text),
        ("Phone number", "phone" in transcript_text or "four zero seven" in transcript_text),
        ("Email address", "email" in transcript_text or "sarah dot johnson" in transcript_text),
        ("Address", "address" in transcript_text or "maple street" in transcript_text),
        ("Pharmacy information", "pharmacy" in transcript_text or "cvs" in transcript_text),
        ("Medication information", "metformin" in transcript_text or "prescription" in transcript_text),
        ("Appointment details", "tuesday" in transcript_text or "appointment" in transcript_text),
    ]

    collected_count = sum(1 for _, condition in checks if condition)
    total_count = len(checks)
    completion_percent = round((collected_count / total_count) * 100)

    checklist = "\n".join(checkbox(condition, label) for label, condition in checks)

    return checklist, collected_count, total_count, completion_percent


def calculate_quality_score(outcome, no_speech_events, agent_messages, athena_messages, completion_percent):
    score = 100

    if "Completed" not in outcome:
        score -= 25

    if no_speech_events:
        score -= min(no_speech_events * 10, 30)

    if agent_messages == 0:
        score -= 20

    if athena_messages == 0:
        score -= 20

    if completion_percent < 25:
        score -= 15
    elif completion_percent < 50:
        score -= 8

    return max(score, 0)


def analyze_warnings(transcript):
    lines = transcript.splitlines() if transcript else []
    warnings = []

    fallback_phrases = [
        "Could you help me with that, please?",
        "I am sorry, I did not catch that. Could you repeat that?",
        "I still cannot hear you clearly. Could you say that one more time?",
    ]

    for index, line in enumerate(lines):
        if "[No speech detected]" in line:
            warnings.append("⚠️ No speech was detected during part of the call.")

        if line.startswith("Athena:") and any(phrase in line for phrase in fallback_phrases):
            previous_line = lines[index - 1] if index > 0 else "No previous agent message."
            warnings.append(
                "⚠️ Athena used a fallback response. Possible unclear question or speech recognition issue.\n"
                f"   Previous turn: {previous_line}\n"
                f"   Athena response: {line}"
            )

    if not warnings:
        return "✓ No major conversation warnings detected."

    unique_warnings = []
    for warning in warnings:
        if warning not in unique_warnings:
            unique_warnings.append(warning)

    return "\n".join(unique_warnings)


def build_outcome_summary(outcome, no_speech_events, agent_messages, athena_messages):
    if outcome == "Completed successfully":
        return "The call completed successfully and Athena ended the conversation cleanly."

    if outcome == "Completed after agent ended the call":
        return "The call completed after the agent ended the conversation."

    if outcome == "Ended after repeated no-speech events":
        return "The call ended after Athena detected repeated no-speech events."

    if no_speech_events > 0:
        return "The call included speech recognition gaps, but Athena continued handling the conversation."

    if agent_messages > 0 and athena_messages > 0:
        return "The call included a two-way exchange between the agent and Athena."

    return "The call report was generated from the available transcript data."


def generate_call_report(outcome):
    report_file = datetime.now().strftime("reports/call_report_%Y%m%d_%H%M%S.txt")

    if os.path.exists(TRANSCRIPT_FILE):
        with open(TRANSCRIPT_FILE, "r") as file:
            transcript = file.read().strip()
    else:
        transcript = "No transcript found."

    lines = transcript.splitlines() if transcript else []
    total_turns = len(lines)
    agent_messages = sum(1 for line in lines if line.startswith("Agent:"))
    athena_messages = sum(1 for line in lines if line.startswith("Athena:"))
    no_speech_events = sum(1 for line in lines if "[No speech detected]" in line)
    duration_seconds = int((datetime.now() - CALL_START_TIME).total_seconds())

    scenario_display_name = get_scenario_display_name()
    collected_information, collected_count, total_fields, completion_percent = analyze_collected_information(transcript)
    outcome_summary = build_outcome_summary(
        outcome,
        no_speech_events,
        agent_messages,
        athena_messages,
    )
    quality_score = calculate_quality_score(
        outcome,
        no_speech_events,
        agent_messages,
        athena_messages,
        completion_percent,
    )
    warnings = analyze_warnings(transcript)

    status_icon = "✅" if "Completed" in outcome else "⚠️"

    report = f"""
====================================
ATHENA CALL REPORT
====================================

Call Date:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Scenario:
{scenario_display_name}

Scenario File:
{VOICE_SCENARIO_FILE}

Status:
{status_icon} {outcome}

Duration:
{duration_seconds} seconds

Conversation Statistics:
------------------------------------
Total Turns: {total_turns}
Agent Messages: {agent_messages}
Athena Responses: {athena_messages}
No-Speech Events: {no_speech_events}

Patient Information Collected:
------------------------------------
Collected: {collected_count} / {total_fields} fields ({completion_percent}%)

{collected_information}

Call Quality:
------------------------------------
Overall Score: {quality_score}/100

Warnings:
------------------------------------
{warnings}

Outcome Summary:
------------------------------------
{outcome_summary}

Transcript File:
------------------------------------
{TRANSCRIPT_FILE}

Transcript:
------------------------------------
{transcript}
====================================
""".strip()

    with open(report_file, "w") as file:
        file.write(report)

    print(f"Call report saved to: {report_file}")
    return report_file


def twiml_response(response):
    return Response(str(response), mimetype="text/xml")


@app.route("/voice", methods=["GET", "POST"])
def voice():
    response = VoiceResponse()
    global CALL_START_TIME, CALL_OUTCOME, NO_SPEECH_COUNT
    CALL_START_TIME = datetime.now()
    CALL_OUTCOME = "In Progress"
    NO_SPEECH_COUNT = 0
    scenario_file = request.args.get("scenario") or request.form.get("scenario")
    if scenario_file:
        set_voice_scenario(scenario_file)

    opening_message = get_opening_message()
    save_turn("Athena", opening_message)

    gather = Gather(
        input="speech",
        action=f"/process_speech?scenario={VOICE_SCENARIO_FILE}",
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
    global NO_SPEECH_COUNT, CALL_OUTCOME
    scenario_file = request.args.get("scenario") or request.form.get("scenario")
    if scenario_file:
        set_voice_scenario(scenario_file)

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
            CALL_OUTCOME = "Ended after repeated no-speech events"
            generate_call_report(CALL_OUTCOME)
            response.say(closing_message, voice="alice", language="en-US")
            response.hangup()
            return twiml_response(response)

    else:
        NO_SPEECH_COUNT = 0

        if "thank you" in speech_text or "thanks" in speech_text or "goodbye" in speech_text or "bye" in speech_text:
            closing_message = "You're welcome. Thank you for your time. Goodbye."
            save_turn("Athena", closing_message)
            CALL_OUTCOME = "Completed after agent ended the call"
            generate_call_report(CALL_OUTCOME)
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
        CALL_OUTCOME = "Completed successfully"
        generate_call_report(CALL_OUTCOME)
        response.say(reply, voice="alice", language="en-US")
        response.hangup()
        return twiml_response(response)

    gather = Gather(
        input="speech",
        action=f"/process_speech?scenario={VOICE_SCENARIO_FILE}",
        method="POST",
        speech_timeout="auto",
        timeout=5,
    )

    gather.say(reply, voice="alice", language="en-US")
    response.append(gather)

    response.pause(length=1)
    response.redirect(f"/process_speech?scenario={VOICE_SCENARIO_FILE}", method="POST")

    return twiml_response(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
