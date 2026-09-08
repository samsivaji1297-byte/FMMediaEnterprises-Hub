import os
import datetime
from zoneinfo import ZoneInfo
from google import genai

OUTPUT_DIR = "WritingFactory/Mindset"
MODEL_NAME = "gemini-3.6-flash"

def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)

def generate_mindset(client):
    prompt = """
Write 250–350 words of minimal, operational mindset guidance.

Constraints:
- Tone: calm, practical, grounded.
- Focus on: mentality, daily execution, cognitive hygiene, emotional regulation, decision clarity.
- Everyday-readable: no mythic language, no grandiose framing.
- Use simple, direct sentences.
- Break into 3–4 short paragraphs.
- Insert a blank line between each paragraph.
- No headings, no bullet points, no lists.
- No formatting.
"""

    chat = client.chats.create(model=MODEL_NAME)
    resp = chat.send_message(prompt)

    text = resp.candidates[0].content.parts[0].text.strip()
    text = text.replace("\n", "\n\n")

    return text

def save_output(text):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.datetime.now(ZoneInfo("Australia/Sydney")).strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{OUTPUT_DIR}/Mindset_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved mindset writing: {filename}")

def main():
    client = get_client()
    text = generate_mindset(client)
    save_output(text)

if __name__ == "__main__":
    main()
