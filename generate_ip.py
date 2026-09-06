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

# --- Save IP to its own .md file ---
def save_ip(ip_text):
    name = ip_text.split("\n")[0].strip()
    filename = f"ip-factory/{name.replace(' ', '_')}.md"

    with open(filename, "w") as f:
        f.write(ip_text)

    return filename

# --- Append to MASTER_IP.md ---
def update_master_list(ip_text):
    name = ip_text.splitlines()[0]
    definition = ip_text.splitlines()[1]

    with open("ip-factory/MASTER_IP.md", "a") as f:
        f.write(f"- {name} — {definition}\n")

# --- Commit changes ---
def git_commit(filename):
    os.system(f"git add {filename} ip-factory/MASTER_IP.md")
    os.system(f'git commit -m "Add new IP framework: {filename}"')

# --- Run the engine ---
if __name__ == "__main__":
    ip = generate_ip()
    filename = save_ip(ip)
    update_master_list(ip)
    git_commit(filename)
