import os
import datetime
from zoneinfo import ZoneInfo
from google import genai

OUTPUT_DIR = "WritingFactory/FreeFall"
MODEL_NAME = "gemini-3.6-flash"

def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)

def generate_freefall(client):
    prompt = """
Generate 300–400 words of free-fall writing in the user's sovereign identity tone.

Constraints:
- Stream-of-consciousness.
- Break the writing into 3–5 natural paragraphs.
- Insert a blank line between each paragraph.
- Blend mythic, clinical, psychological, operational, and strategic tones.
- Must align with: Mental Sovereignty, Identity Mechanics, Operator Autonomy, Empire Architecture.
- Pure flow, no headings, no bullet points.
"""

    chat = client.chats.create(model=MODEL_NAME)
    resp = chat.send_message(prompt)

    # Extract text from the response
    text = resp.candidates[0].content.parts[0].text.strip()

    # Guarantee Markdown paragraph spacing
    text = text.replace("\n", "\n\n")

    return text

def save_output(text):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Sydney-local timestamp
    timestamp = datetime.datetime.now(ZoneInfo("Australia/Sydney")).strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{OUTPUT_DIR}/FreeFall_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved free-fall writing: {filename}")

def main():
    client = get_client()
    text = generate_freefall(client)
    save_output(text)

if __name__ == "__main__":
    main()
