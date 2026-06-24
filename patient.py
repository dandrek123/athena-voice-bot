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

    if "member id" in message or "policy number" in message or "subscriber id" in message:
        return "Yes, my member ID is B C B S one two three four five six."

    if "happy to help" in message or "how can i help" in message or "how may i help" in message:
        if "registration" in current_persona.lower() or "new patient" in current_persona.lower():
            return "I would like to register as a new patient."
        return "I would like to schedule an appointment."

    if "what brings you in" in message or "reason for" in message or "reason for your visit" in message:
        return "I would like to schedule a routine appointment with the clinic."

    if "emergency" in message or "chest pain" in message or "trouble breathing" in message:
        return "No, this is not an emergency. I am just trying to schedule a regular appointment."

    if "medication" in message or "refill" in message or "prescription" in message:
        return "I need a refill for my Metformin, five hundred milligrams. I take it twice a day."

    if "pharmacy" in message:
        return "Please send it to the CVS on Main Street."

    if "name" in message:
        return "My name is Sarah Johnson."

    if "date of birth" in message or "birth" in message or "dob" in message:
        return "My date of birth is January tenth, nineteen ninety two."

    if "insurance" in message:
        return "I have Blue Cross Blue Shield insurance."

    if "email" in message:
        return "My email is sarah dot johnson at email dot com."

    if "address" in message or "where do you live" in message:
        return "My address is one two three Maple Street, Orlando, Florida."

    if "phone" in message or "number" in message:
        return "My phone number is four zero seven, three three four, five seven three two."

    if "cancel" in message:
        return "I would like to cancel my appointment if possible."

    if "reschedule" in message or "change my appointment" in message:
        return "I would like to reschedule my appointment to next Tuesday morning if possible."

    if "day" in message or "date" in message or "time" in message or "come in" in message or "appointment" in message:
        return "Next Tuesday morning would work for me if you have availability."

    if "office hours" in message or "hours" in message or "open" in message:
        return "Could you tell me what your office hours are?"

    if "symptom" in message or "pain" in message or "hurt" in message:
        return "I have had mild knee pain for about two weeks, but it is not an emergency."

    if "anything else" in message or "is that all" in message:
        return "No, that is all. Thank you."

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