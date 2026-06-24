# Athena Voice Bot Simulator

AI-powered healthcare voice patient simulator built with Python, Flask, Twilio, and Google Gemini.

Athena simulates realistic patient phone calls to healthcare providers for testing appointment scheduling, prescription refills, insurance updates, patient registration, and other office workflows using conversational AI.

---

## Features

- Interactive healthcare voice conversations
- Six healthcare patient workflows
- Dynamic patient personas
- Command-line scenario selection
- Twilio outbound phone calls
- Flask webhook server
- Speech-to-text conversations
- Transcript logging
- Conversation memory
- No-speech retry handling
- Automatic call ending
- Mock mode for offline development
- Google Gemini AI integration
- Modular scenario-based architecture

---

## Supported Voice Workflows

- Appointment Scheduling
- New Patient Registration
- Prescription Refill
- Insurance Update
- Appointment Cancellation
- Appointment Rescheduling

---

## Architecture

```text
                Phone Call
                     │
                     ▼
             Twilio Voice API
                     │
                     ▼
            Flask Webhook Server
                     │
                     ▼
          Scenario / Patient Persona
                     │
                     ▼
         Patient Response Engine
                     │
                     ▼
      Speech Response + Transcript Log
```

---

## Project Structure

```text
athena-voice-bot/
├── scenarios/
│   ├── insurance_patient.txt
│   ├── new_patient.txt
│   ├── refill_patient.txt
│   ├── cancel_patient.txt
│   ├── reschedule_patient.txt
│   └── new_registration_patient.txt
│
├── call_runner.py
├── twiml_server.py
├── patient.py
├── logger.py
├── summarizer.py
├── main.py
├── test_call.py
├── test_gemini.py
├── requirements.txt
├── ROADMAP.md
└── .env.example
```

---

## Installation

```bash
git clone https://github.com/dandrek123/athena-voice-bot.git

cd athena-voice-bot

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_api_key_here

USE_MOCK_MODE=true

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token

TWILIO_PHONE_NUMBER=+10000000000
TEST_TO_PHONE_NUMBER=+10000000000

VOICE_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app/voice

VOICE_SCENARIO_FILE=new_patient.txt
```

---

## Running Athena

Start the Flask webhook:

```bash
python twiml_server.py
```

Place a voice call:

```bash
python call_runner.py --scenario appointment
```

Available scenarios:

```bash
python call_runner.py --scenario appointment
python call_runner.py --scenario refill
python call_runner.py --scenario insurance
python call_runner.py --scenario cancel
python call_runner.py --scenario reschedule
python call_runner.py --scenario registration
```

---

## Example Conversation

```text
Athena: Hello, this is Athena. I would like to schedule an appointment.

Agent: What is your name?

Athena: My name is Sarah Johnson.

Agent: What day would you like to come in?

Athena: Next Tuesday morning would work for me if you have availability.

Agent: What insurance do you have?

Athena: I have Blue Cross Blue Shield insurance.

Agent: What is your date of birth?

Athena: My date of birth is January tenth, nineteen ninety two.

Agent: Anything else?

Athena: No, that is all. Thank you.
```

---

## Technologies Used

- Python
- Flask
- Twilio Voice API
- Google Gemini API
- Python Dotenv
- Speech Recognition
- Prompt Engineering
- REST Webhooks

---

## Current Capabilities

- Voice-based patient simulation
- Multiple healthcare conversation workflows
- Scenario-based personas
- Transcript generation
- Interactive speech conversations
- Command-line scenario switching
- Mock mode for offline testing
- Modular architecture for future AI expansion

---

## Roadmap

- Automatic call reports
- Conversation quality scoring
- Live Gemini-powered conversations
- Web dashboard
- Recording management
- Additional healthcare workflows
- Multi-language conversations
- Pretty Good AI Challenge submission

---

## Author

**D'Andre Knight**

Computer Science graduate focused on Software Engineering, Artificial Intelligence, Automation, Cybersecurity, and Voice AI.

GitHub: https://github.com/dandrek123
