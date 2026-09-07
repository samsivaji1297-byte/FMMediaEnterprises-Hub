import os
from google import genai
from google.genai.types import Content, Part

IP_DIR = "IPFactory"
MASTER_FILE = os.path.join(IP_DIR, "!MASTER_IP.md")
MODEL_NAME = "gemini-1.5-flash"  # or your current model

def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)

def load_master_lines():
    if not os.path.exists(MASTER_FILE):
        return []
    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        return f.readlines()

def save_master_lines(lines):
    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

def generate_definition(client, name: str) -> str:
    prompt = f"""
Generate a one-sentence definition for the following sovereign IP framework name:

{name}

Constraints:
- One sentence only.
- Tone may be mythic, clinical, psychological, operational, or strategic.
- Must align with: Mental Sovereignty, Mental Mastery, Identity Mechanics,
  Operator Autonomy, Internal Gravity, Cognitive Territory, Mythic Identity, Empire Architecture.
- No extra commentary, no headings, no bullet points. Just the sentence.
"""
    chat = client.chats.create(model=MODEL_NAME)
    resp = chat.send_message(Content(parts=[Part.from_text(prompt)]))
    text = resp.output_text.strip()
    # Safety: ensure it's one line
    return " ".join(text.splitlines()).strip()

def repair_ip_file(client, path: str) -> str | None:
    """
    Returns the definition if repaired, else None.
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return None

    # Expect format:
    # line 0: "# Name"
    # line 1: definition (may be missing)
    header = lines[0].strip()
    if not header.startswith("# "):
        return None

    name = header[2:].strip()

    # If we already have a non-empty second line, skip
    if len(lines) > 1 and lines[1].strip():
        return None

    # Need to generate definition
    definition = generate_definition(client, name)
    if len(lines) > 1:
        lines[1] = definition + "\n"
    else:
        lines.append(definition + "\n")

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Repaired definition for: {name}")
    return definition

def repair_master_entry(master_lines, name: str, definition: str):
    """
    Update the line in !MASTER_IP.md that matches the name.
    Expected format:
    - Name — definition
    or
    - Name
    """
    updated = False
    for i, line in enumerate(master_lines):
        stripped = line.strip()
        if stripped.startswith("- "):
            # Remove leading "- "
            content = stripped[2:]
            # Split on em dash or hyphen
            if content.startswith(name):
                # Replace entire line with proper format
                master_lines[i] = f"- {name} — {definition}\n"
                updated = True
                break
    if updated:
        print(f"Updated master entry for: {name}")
    return updated

def main():
    client = get_client()
    master_lines = load_master_lines()
    changed_master = False

    for filename in os.listdir(IP_DIR):
        if not filename.endswith(".md"):
            continue
        if filename == "!MASTER_IP.md":
            continue

        path = os.path.join(IP_DIR, filename)
        definition = repair_ip_file(client, path)
        if definition:
            # Extract name from header again
            with open(path, "r", encoding="utf-8") as f:
                header = f.readline().strip()
            name = header[2:].strip()
            if repair_master_entry(master_lines, name, definition):
                changed_master = True

    if changed_master:
        save_master_lines(master_lines)
    else:
        print("No master entries needed repair.")

if __name__ == "__main__":
    main()
