from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

conversation_history = []
current_persona = ""

USE_MOCK_MODE = os.getenv("USE_MOCK_MODE", "false").lower() == "true"

def load_persona(filename):
    global current_persona
    conversation_history.clear()

    with open(f"scenarios/{filename}", "r") as f:
        current_persona = f.read()

def mock_response(clinic_message):
    message = clinic_message.lower()

    if "happy to help" in message or "how can i help" in message:
        return "I would like to schedule an appointment."
    
    if "how may i help" in message:
        return "I would like to schedule an appointment."

    if "what brings you in" in message:
        return "I'm calling because I need help with my request today."

    if "medication" in message or "refill" in message:
        return "I need a refill for my prescription medication."

    if "name" in message:
        return "My name is Sarah Johnson."

    if "date of birth" in message or "birth" in message or "dob" in message:
        return "My date of birth is January tenth, nineteen ninety two."

    if "insurance" in message:
        return "I have Blue Cross Blue Shield insurance."

    if "day" in message or "date" in message or "time" in message or "come in" in message or "appointment" in message:
        return "Next Tuesday morning would work for me if you have availability."

    if "phone" in message or "number" in message:
        return "My phone number is four zero seven, three three four, five seven three two."

    if "email" in message:
        return "My email is sarah dot johnson at email dot com."

    if "reason" in message or "visit" in message or "symptom" in message:
        return "I would like to schedule a routine appointment with the clinic."

    return "Could you help me with that, please?"


def patient_response(clinic_message):
    conversation_history.append(f"Clinic: {clinic_message}")

    prompt = current_persona + "\n\n" + "\n".join(conversation_history)

    if USE_MOCK_MODE:
        reply = mock_response(clinic_message)
        conversation_history.append(f"Patient: {reply}")
        return reply

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        reply = response.text.strip().replace("Patient:", "").strip()

    except Exception as error:
        reply = (
            "I'm sorry, I'm having trouble responding right now. "
            "I would still like to continue with my request."
        )
        print(f"\n[Gemini error handled: {error}]\n")

    conversation_history.append(f"Patient: {reply}")

    return reply