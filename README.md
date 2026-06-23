# Athena Voice Bot Simulator

AI-powered healthcare patient simulator built with Python and Google Gemini.

## Features

- Multiple patient personas
- Dynamic scenario loading
- Conversation memory
- Transcript logging
- Automated conversation summaries
- Mock mode for offline testing
- Gemini AI integration

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
├── test_gemini.py
├── test_call.py
├── requirements.txt
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
```

## Run

```bash
python main.py
```

## Example

```text
Select Scenario
1. Insurance Patient
2. New Patient
3. Refill Patient

Choice: 2

Loaded scenario: New Patient

Clinic: What brings you in today?

Patient:
I'm calling because I need help with my request today.
```

## Technologies Used

- Python
- Google Gemini API
- Python Dotenv
- Twilio
- File-Based Logging
- Prompt Engineering

## Current Features

### Patient Simulation
- New patient registration
- Prescription refill requests
- Insurance update scenarios
- Dynamic persona loading

### Reporting
- Conversation transcript logging
- Automated conversation summaries
- Local fallback summaries
- Mock mode support

### Development Features
- Environment variable configuration
- Scenario-based testing
- Offline testing mode
- Modular project structure

## Future Improvements

- Voice calling with Twilio
- Real-time AI conversations
- Additional patient personas
- Advanced QA reports
- Healthcare workflow testing
- Appointment scheduling scenarios
- Multi-language patient support

## Author

**D'Andre Knight**

Computer Science Graduate focused on Software Engineering, AI, Automation, and Cybersecurity.

GitHub: https://github.com/dandrek123
