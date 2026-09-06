import os
from google import genai

# --- Gemini Client ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Load existing IP names dynamically ---
def load_existing_ip_names():
    master_path = "IPFactory/!MASTER_IP.md"
    if not os.path.exists(master_path):
        return []

    existing_names = []
    with open(master_path, "r") as f:
        for line in f.readlines():
            if line.startswith("- "):
                # Extract name before the em dash
                name = line.split("—")[0].replace("- ", "").strip()
                existing_names.append(name)
    return existing_names


# --- Build dynamic prompt ---
def build_prompt(existing_names):
    existing_list = "\n".join(f"- {name}" for name in existing_names)

    prompt = f"""
Existing IP names:
{existing_list}

Generate ONE new sovereign IP framework that is NOT any of the above.

Format:
<Framework Name>
<One-line definition>

Rules:
- The name must be between 2 and 8 words.
- The definition must be one sentence.
- The IP must align with the user's identity architecture:
  Mental Sovereignty, Mental Mastery, Identity Mechanics,
  Operator Autonomy, Internal Gravity, Cognitive Territory,
  Mythic Identity, Empire Architecture.
- Do NOT generate explanations, doctrine, or multi-paragraph content.
"""
    return prompt


# --- Generate IP ---
def generate_ip(prompt):
    chat = client.chats.create(model="gemini-3.6-flash")
    response = chat.send_message(prompt)
    return response.text.strip()


# --- Parse Gemini output ---
def parse_ip(ip_text):
    # Case 1: "Name — Definition"
    if "—" in ip_text:
        parts = ip_text.split("—")
        name = parts[0].strip()
        definition = parts[1].strip()
        return name, definition

    # Case 2: two-line format
    lines = ip_text.splitlines()
    name = lines[0].strip()
    definition = lines[1].strip() if len(lines) > 1 else ""
    return name, definition


# --- Save IP file ---
def save_ip(name, definition):
    filename = f"IPFactory/{name.replace(' ', '_')}.md"
    with open(filename, "w") as f:
        f.write(f"# {name}\n{definition}\n")
    return filename


# --- Update master list ---
def update_master_list(name, definition):
    with open("IPFactory/!MASTER_IP.md", "a") as f:
        f.write(f"- {name} — {definition}\n")


# --- Commit changes ---
def git_commit(filename):
    os.system(f"git add {filename} IPFactory/!MASTER_IP.md")
    os.system(f'git commit -m "Add new IP framework: {filename}"')


# --- Run engine ---
if __name__ == "__main__":
    existing_names = load_existing_ip_names()
    prompt = build_prompt(existing_names)
    raw_ip = generate_ip(prompt)
    name, definition = parse_ip(raw_ip)
    filename = save_ip(name, definition)
    update_master_list(name, definition)
    git_commit(filename)
