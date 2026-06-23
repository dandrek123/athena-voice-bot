import os

from patient import patient_response, load_persona
from logger import save_message
from summarizer import summarize_conversation, save_summary

SCENARIOS_FOLDER = "scenarios"
conversation_log = []


def format_scenario_name(filename):
    name = filename.replace(".txt", "")
    name = name.replace("_", " ").replace("-", " ")
    return name.title()


def get_scenario_files():
    return sorted(
        file
        for file in os.listdir(SCENARIOS_FOLDER)
        if file.endswith(".txt")
    )


def choose_scenario():
    scenario_files = get_scenario_files()

    if not scenario_files:
        raise FileNotFoundError("No .txt scenario files found in the scenarios folder.")

    print("Select Scenario")

    for index, filename in enumerate(scenario_files, start=1):
        print(f"{index}. {format_scenario_name(filename)}")

    choice = input("Choice: ").strip()

    if choice.isdigit():
        selected_index = int(choice) - 1

        if 0 <= selected_index < len(scenario_files):
            selected_file = scenario_files[selected_index]
            load_persona(selected_file)
            print(f"Loaded scenario: {format_scenario_name(selected_file)}")
            return

    default_file = scenario_files[0]
    print(f"Invalid choice. Loading default scenario: {format_scenario_name(default_file)}")
    load_persona(default_file)


choose_scenario()

print("\nAI Patient Started")
print("Type 'exit' to quit\n")

while True:
    clinic = input("Clinic: ")

    if clinic.lower() == "exit":
        if conversation_log:
            transcript_text = "\n".join(conversation_log)

            print("\nGenerating conversation summary...\n")

            summary = summarize_conversation(transcript_text)

            print(summary)
            report_file = save_summary(summary)
            print(f"\nSummary saved to: {report_file}")

        break

    save_message("Clinic", clinic)
    conversation_log.append(f"Clinic: {clinic}")

    reply = patient_response(clinic)

    save_message("Patient", reply)
    conversation_log.append(f"Patient: {reply}")

    print("\nPatient:")
    print(reply)
    print()