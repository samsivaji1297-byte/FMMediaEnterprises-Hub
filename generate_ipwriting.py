import os
import random
import datetime
from google import genai
from google.genai.types import Content, Part

IP_DIR = "IPFactory"
OUTPUT_DIR = "WritingFactory/IPDriven"
MODEL_NAME = "gemini-1.5-flash"

def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)

def load_ips():
    ips = []
    for filename in os.listdir(IP_DIR):
        if filename.endswith(".md") and filename != "!MASTER_IP.md":
            path = os.path.join(IP_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                header = f.readline().strip()
                if header.startswith("# "):
                    ips.append(header[2:].strip())
    return ips

def generate_ip_writing(client, ip_name):
    prompt = f"""
Write 300–400 words expanding the following sovereign IP framework:

{ip_name}

Constraints:
- Blend mythic, clinical, psychological, operational, and strategic tones.
- Must align with: Mental Sovereignty, Identity Mechanics, Operator Autonomy, Empire Architecture.
- Produce structured writing but no headings.
- No bullet points.
- No lists.
- No formatting.
"""

    chat = client.chats.create(model=MODEL_NAME)
    resp = chat.send_message(Content(parts=[Part.from_text(prompt)]))
    return resp.output_text.strip()

def save_output(ip_name, text):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = ip_name.replace(" ", "_")
    filename = f"{OUTPUT_DIR}/{safe_name}_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {ip_name} — Writing Expansion\n\n{text}")

    print(f"Saved IP-driven writing: {filename}")

def main():
    client = get_client()
    ips = load_ips()
    if not ips:
        raise RuntimeError("No IPs found in IPFactory")

    ip_name = random.choice(ips)
    text = generate_ip_writing(client, ip_name)
    save_output(ip_name, text)

if __name__ == "__main__":
    main()
