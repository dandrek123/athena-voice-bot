from datetime import datetime
import os

os.makedirs("transcripts", exist_ok=True)

def save_message(role, message):
    filename = datetime.now().strftime("transcripts/call_%Y%m%d.txt")

    with open(filename, "a") as f:
        f.write(f"{role}: {message}\n")