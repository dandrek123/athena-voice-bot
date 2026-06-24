# Athena Voice Bot Simulator

AI-powered healthcare patient simulator built with Python, Google Gemini, Twilio, and Flask.

## Features

- Multiple patient personas
- Dynamic scenario loading
- Conversation memory
- Transcript logging
- Automated conversation summaries
- Mock mode for offline testing
- Gemini AI integration
- Twilio outbound phone calls
- Flask webhook for voice responses
- Interactive speech-based conversations
- No-speech retry handling
- Automatic call ending logic

## Project Structure

```text
athena-voice-bot/
├── scenarios/
│   ├── insurance_patient.txt
│   ├── new_patient.txt
│   └── refill_patient.txt
├── logger.py
├── patient.py
├── summarizer.py
├── main.py
├── twiml_server.py
├── call_runner.py
├── test_gemini.py
├── test_call.py
├── requirements.txt
├── ROADMAP.md
└── .env.example
```

## Installation

```bash
git clone https://github.com/dandrek123/athena-voice-bot.git
cd athena-voice-bot

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
USE_MOCK_MODE=true

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+10000000000
TEST_TO_PHONE_NUMBER=+10000000000
VOICE_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.dev/voice
VOICE_SCENARIO_FILE=new_patient.txt
```

## Run Text Simulator

```bash
python main.py
```

## Run Voice Bot

Start the Flask voice server:

```bash
python twiml_server.py
```

Expose the local server with ngrok:

```bash
ngrok http 5001
```

Update `VOICE_WEBHOOK_URL` in `.env` using the ngrok URL, then start a test call:

```bash
python call_runner.py
```

## Example Voice Conversation

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

## Technologies Used

- Python
- Google Gemini API
- Twilio Voice
- Flask
- Python Dotenv
- File-Based Logging
- Prompt Engineering

## Current Features

### Patient Simulation

- New patient registration
- Prescription refill requests
- Insurance update scenarios
- Appointment scheduling conversations
- Scenario-based persona loading
- Mock patient responses for offline testing

### Voice Calling

- Outbound phone calls with Twilio
- Flask-based TwiML webhook
- Speech input handling with Twilio Gather
- Voice responses using Twilio text-to-speech
- Automatic retry handling when speech is not detected
- Graceful call ending after completed conversations

### Reporting

- Conversation transcript logging
- Automated conversation summaries
- Local fallback summaries
- Mock mode support

## Future Improvements

- Gemini-powered live phone responses
- Additional patient personas
- Automated bug report generation
- Audio recording download support
- Healthcare workflow testing
- Appointment cancellation and rescheduling flows
- Multi-language patient support

## Author

**D'Andre Knight**

Computer Science Graduate focused on Software Engineering, AI, Automation, and Cybersecurity.

GitHub: https://github.com/dandrek123
