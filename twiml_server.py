import os
from datetime import datetime

from flask import Flask, Response, abort, render_template, request
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


# Dashboard routes
def get_report_files():
    report_files = []

    for filename in os.listdir("reports"):
        if filename.startswith("call_report_") and filename.endswith(".txt"):
            report_files.append(filename)

    return sorted(report_files, reverse=True)


def parse_report_summary(filename):
    path = os.path.join("reports", filename)

    with open(path, "r") as file:
        content = file.read()

    def get_value(label):
        lines = content.splitlines()
        for i, line in enumerate(lines):
            stripped_line = line.strip()

            if stripped_line == label and i + 1 < len(lines):
                return lines[i + 1].strip()

            if stripped_line.startswith(label):
                value = stripped_line.replace(label, "", 1).strip()
                if value:
                    return value

        return "Unknown"

    return {
        "filename": filename,
        "scenario": get_value("Scenario:"),
        "status": get_value("Status:"),
        "duration": get_value("Duration:"),
        "quality": get_value("Overall Score:"),
        "date": get_value("Call Date:"),
        "warnings": "⚠️" if "⚠️" in content else "✓",
    }


def calculate_analytics():
    report_files = get_report_files()
    reports = [parse_report_summary(file) for file in report_files]

    valid_reports = [report for report in reports if report["scenario"] != "Unknown"]
    total_calls = len(valid_reports)

    completed_calls = sum(
        1 for report in valid_reports
        if "Completed" in report["status"]
    )

    warning_count = sum(
        1 for report in valid_reports
        if report["warnings"] == "⚠️"
    )

    quality_scores = []
    durations = []
    scenario_counts = {}

    for report in valid_reports:
        quality_text = report["quality"].replace("/100", "").strip()
        if quality_text.isdigit():
            quality_scores.append(int(quality_text))

        duration_text = report["duration"].replace("seconds", "").strip()
        if duration_text.isdigit():
            durations.append(int(duration_text))

        scenario = report["scenario"]
        scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1

    average_quality = round(sum(quality_scores) / len(quality_scores), 1) if quality_scores else 0
    average_duration = round(sum(durations) / len(durations), 1) if durations else 0
    success_rate = round((completed_calls / total_calls) * 100, 1) if total_calls else 0

    most_common_scenario = "None"
    if scenario_counts:
        most_common_scenario = max(scenario_counts, key=scenario_counts.get)

    return {
        "total_calls": total_calls,
        "completed_calls": completed_calls,
        "warning_count": warning_count,
        "average_quality": average_quality,
        "average_duration": average_duration,
        "success_rate": success_rate,
        "most_common_scenario": most_common_scenario,
        "scenario_counts": scenario_counts,
    }


@app.route("/dashboard")
def dashboard():
    report_files = get_report_files()
    reports = [parse_report_summary(file) for file in report_files]
    return render_template("dashboard.html", reports=reports)


@app.route("/analytics")
def analytics():
    data = calculate_analytics()
    return render_template("analytics.html", data=data)


@app.route("/")
def home():
    return dashboard()


@app.route("/report/<report_name>")
def view_report(report_name):
    safe_reports = get_report_files()

    if report_name not in safe_reports:
        abort(404)

    report_path = os.path.join("reports", report_name)

    with open(report_path, "r") as file:
        report_content = file.read()

    return render_template(
        "report.html",
        report_name=report_name,
        report_content=report_content,
    )


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
