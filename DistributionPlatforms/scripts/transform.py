import os
import time
import json
import glob
from google import genai
from google.genai import errors

# Initialize client using GEMINI_API_KEY from environment
client = genai.Client()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INPUT_DIR = os.path.join(BASE_DIR, "WritingFactory")
OUTPUT_FILE = os.path.join(BASE_DIR, "dist", "latest_payload.json")

SYSTEM_INSTRUCTION = """
You are a content transformation engine. Convert the input raw draft into a Substack Note format.
Return ONLY valid JSON with a single key "substack_note". Do not wrap in markdown block quotes.
"""

def generate_with_retry(model, contents, config, max_retries=3):
    """Calls Gemini API with backoff handling for 429 Rate Limits."""
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
        except errors.ClientError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 20  # Wait 20s, then 40s...
                print(f"Rate limit hit (429). Waiting {wait_time}s before retrying (Attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise e

def process_ready_files():
    files = glob.glob(os.path.join(INPUT_DIR, "*.md"))
    if not files:
        print("No raw markdown files found in WritingFactory/. Skipping.")
        return

    # Take the latest modified file
    latest_file = max(files, key=os.path.path.getmtime)
    print(f"Processing payload for: {os.path.relpath(latest_file, BASE_DIR)}")

    with open(latest_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    response = generate_with_retry(
        model="gemini-2.5-flash",  # Using high-throughput flash model
        contents=f"Transform this content into a Substack Note:\n\n{raw_text}",
        config={"system_instruction": SYSTEM_INSTRUCTION}
    )

    clean_text = response.text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text.replace("```json", "", 1).rsplit("```", 1)[0].strip()
    elif clean_text.startswith("```"):
        clean_text = clean_text.replace("```", "", 1).rsplit("```", 1)[0].strip()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(clean_text)

    print(f"Payload successfully output to {os.path.relpath(OUTPUT_FILE, BASE_DIR)}")

if __name__ == "__main__":
    process_ready_files()
