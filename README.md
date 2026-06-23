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

```
athena-voice-bot/
├── scenarios/
├── logger.py
├── patient.py
├── summarizer.py
├── main.py
├── test_gemini.py
├── test_call.py
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

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key
USE_MOCK_MODE=true
```

## Run

```bash
python main.py
```

## Example

```
Select Scenario
1. Insurance Patient
2. New Patient
3. Refill Patient

Clinic: What brings you in today?

Patient:
I'm calling because I need help with my request today.
```

## Future Improvements

- Voice calling with Twilio
- Real-time AI conversations
- Additional patient personas
- Advanced QA reports
- Healthcare workflow testing
