import os
import datetime
import google.generativeai as genai

# 1. Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. Prompt for sovereign IP framework generation
IP_PROMPT = """
You are the Sovereign IP Engine.

Generate ONE new sovereign IP framework.
Format:
1. A powerful, identity-coded name (2–4 words).
2. A one-line definition describing the framework's essence.

The IP must align with:
- Mental Sovereignty
- Mental Mastery
- Identity Mechanics
- Operator Autonomy
- Internal Gravity
- Cognitive Territory
- Mythic Identity
- Empire Architecture

Do NOT generate explanations, doctrine, or multi-paragraph content.
Only:
Name
One-line definition
"""

def generate_ip():
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(IP_PROMPT)
    return response.text.strip()

# 3. Save IP framework to its own .md file
def save_ip(ip_text):
    name = ip_text.split("\n")[0].strip().replace(" ", "_")
    filename = f"ip-factory/{name}.md"

    with open(filename, "w") as f:
        f.write(ip_text)

    return name, filename

# 4. Append to MASTER_IP.md
def update_master_list(name, ip_text):
    with open("ip-factory/MASTER_IP.md", "a") as f:
        f.write(f"\n- {ip_text.splitlines()[0]} — {ip_text.splitlines()[1]}\n")

# 5. Commit changes
def git_commit(filename):
    os.system(f"git add {filename} ip-factory/MASTER_IP.md")
    os.system(f'git commit -m "Add new IP framework: {filename}"')

# 6. Run the engine
if __name__ == "__main__":
    ip = generate_ip()
    name, filename = save_ip(ip)
    update_master_list(name, ip)
    git_commit(filename)
