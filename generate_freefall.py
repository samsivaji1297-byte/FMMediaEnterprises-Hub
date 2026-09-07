import os
import datetime
from google import genai
from google.genai.types import Content, Part

OUTPUT_DIR = "WritingFactory/FreeFall"
MODEL_NAME = "gemini-1.5-flash"

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
- No headings.
- No bullet points.
- No structure.
- Blend mythic, clinical, psychological, operational, and strategic tones.
- Must align with: Mental Sovereignty, Identity Mechanics, Operator Autonomy, Empire Architecture.
- Pure flow, no formatting.
"""

    chat = client.chats.create(model=MODEL_NAME)
    resp = chat.send_message(Content(parts=[Part.from_text(prompt)]))
    return resp.output_text.strip()

def save_output(text):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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
