import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
USE_MOCK_MODE = os.getenv("USE_MOCK_MODE", "false").lower() == "true"


def summarize_conversation(transcript_text):
    prompt = f"""
Analyze this healthcare clinic conversation.

Return:
1. Short summary
2. Patient goal
3. Outcome
4. Possible issues or missing information
5. Suggested bug report items if any

Transcript:
{transcript_text}
"""

    if USE_MOCK_MODE:
        return f"""
Conversation Summary
--------------------
Mock mode is enabled, so this summary was generated locally without using Gemini.

Short summary:
A simulated clinic conversation was completed.

Patient goal:
The patient asked for help with a healthcare-related request.

Outcome:
The conversation ended before the clinic fully resolved the request.

Possible issues or missing information:
- Patient identity was not fully verified.
- The clinic did not collect enough details to complete the request.
- The conversation ended before next steps were confirmed.

Suggested bug report items:
- Missing identity verification flow.
- Missing follow-up questions.
- No clear confirmation or resolution before the conversation ended.

Transcript reviewed:
{transcript_text}
""".strip()

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as error:
        return f"""
Conversation Summary
--------------------
Gemini summary failed, so this fallback summary was generated locally.

Error:
{error}

Short summary:
A simulated clinic conversation was completed.

Patient goal:
The patient asked for help with a healthcare-related request.

Outcome:
The conversation ended before the clinic fully resolved the request.

Possible issues or missing information:
- Patient identity was not fully verified.
- The clinic did not collect enough details to complete the request.
- The conversation ended before next steps were confirmed.

Suggested bug report items:
- Missing identity verification flow.
- Missing follow-up questions.
- No clear confirmation or resolution before the conversation ended.

Transcript reviewed:
{transcript_text}
""".strip()


def save_summary(summary_text):
    os.makedirs("reports", exist_ok=True)

    filename = datetime.now().strftime("reports/report_%Y%m%d_%H%M%S.txt")

    with open(filename, "w") as file:
        file.write(summary_text)

    return filename