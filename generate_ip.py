import os
from google import genai

# --- Gemini Client ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Prompt for sovereign IP framework generation ---
IP_PROMPT = """
Generate ONE new sovereign IP framework.

Format:
<Framework Name>
<One-line definition>

Rules:
- The name must be 2–4 words.
- The definition must be one sentence.
- The IP must align with the user's identity architecture:
  Mental Sovereignty, Mental Mastery, Identity Mechanics,
  Operator Autonomy, Internal Gravity, Cognitive Territory,
  Mythic Identity, Empire Architecture.
- Do NOT generate explanations, doctrine, or multi-paragraph content.
"""

def generate_ip():
    chat = client.chats.create(model="gemini-3.6-flash")
    response = chat.send_message(IP_PROMPT)
    return response.text.strip()


# --- Parse Gemini output into name + definition ---
def parse_ip(ip_text):
    # Case 1: Gemini returns "Name — Definition"
    if "—" in ip_text:
        parts = ip_text.split("—")
        name = parts[0].strip()
        definition = parts[1].strip()
        return name, definition

    # Case 2: Gemini returns two lines
    lines = ip_text.splitlines()
    name = lines[0].strip()
    definition = lines[1].strip() if len(lines) > 1 else ""
    return name, definition


# --- Save IP to its own .md file ---
def save_ip(name, definition):
    filename = f"IPFactory/{name.replace(' ', '_')}.md"
    with open(filename, "w") as f:
        f.write(f"# {name}\n{definition}\n")
    return filename


# --- Append to MASTER_IP.md ---
def update_master_list(name, definition):
    with open("IPFactory/!MASTER_IP.md", "a") as f:
        f.write(f"- {name} — {definition}\n")


# --- Commit changes ---
def git_commit(filename):
    os.system(f"git add {filename} IPFactory/MASTER_IP.md")
    os.system(f'git commit -m "Add new IP framework: {filename}"')


# --- Run the engine ---
if __name__ == "__main__":
    raw_ip = generate_ip()
    name, definition = parse_ip(raw_ip)
    filename = save_ip(name, definition)
    update_master_list(name, definition)
    git_commit(filename)
