import sys
import subprocess
from pathlib import Path
from google.genai import types

# Resolve project root path for clean config imports
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import get_client, call_with_fallback

# --- Configuration & Paths ---
IP_FACTORY_DIR = PROJECT_ROOT / "IPFactory"
MASTER_FILE = IP_FACTORY_DIR / "!MASTER_IP.md"

client = get_client()


def load_existing_ip_names() -> list[str]:
    """Dynamically parses existing IP framework names from MASTER_IP.md."""
    if not MASTER_FILE.exists():
        return []

    existing_names = []
    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("- "):
                name = line.split("—")[0].replace("- ", "").strip()
                if name:
                    existing_names.append(name)
    return existing_names


def build_prompt(existing_names: list[str]) -> str:
    """Constructs systemic identity architecture generation prompt."""
    existing_list = "\n".join(f"- {name}" for name in existing_names)

    return f"""
Existing IP names:
{existing_list}

Generate ONE new sovereign IP framework.

Tone balance:
- The IP may be mythic, clinical, psychological, operational, or strategic.
- Do NOT lock into any single tone. Vary naturally.
- The IP should feel distinct from existing IPs.

Format:
<Framework Name>
<One-line definition>

Rules:
- The name must be between 2 to 8 words.
- The definition must be one sentence.
- The IP must align with the user's identity architecture:
  Mental Sovereignty, Mental Mastery, Identity Mechanics,
  Operator Autonomy, Internal Gravity, Cognitive Territory,
  Mythic Identity, Empire Architecture.
- The IP may be mythic or non-mythic.
- Do NOT generate explanations, doctrine, or multi-paragraph content.
"""


def generate_ip(prompt: str) -> str:
    """Executes prompt against model cascade with disabled automatic function calling warnings."""
    def _api_func_builder(target_model: str):
        def _api_call():
            print(f"Requesting generation using model: {target_model}")
            
            # Disable AFC locally to suppress SDK warning logs
            gen_config = types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )
            
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=gen_config,
            )
            return response.text.strip()
        return _api_call

    return call_with_fallback(_api_func_builder)


def parse_ip(ip_text: str) -> tuple[str, str]:
    """Parses raw text returned from Gemini into Name and Definition strings."""
    lines = [line.strip() for line in ip_text.splitlines() if line.strip()]
    
    # Format Case 1: "Name — Definition"
    if lines and "—" in lines[0]:
        parts = lines[0].split("—", 1)
        return parts[0].strip(), parts[1].strip()

    # Format Case 2: Line 1 = Name, Line 2 = Definition
    name = lines[0] if lines else "Unnamed_Framework"
    definition = lines[1] if len(lines) > 1 else ""
    return name, definition


def save_ip(name: str, definition: str) -> Path:
    """Saves generated IP into a dedicated Markdown file inside IPFactory."""
    IP_FACTORY_DIR.mkdir(parents=True, exist_ok=True)
    
    clean_name = "".join(c if c.isalnum() or c in (" ", "_") else "" for c in name)
    filename = IP_FACTORY_DIR / f"{clean_name.replace(' ', '_')}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {name}\n{definition}\n")
    return filename


def update_master_list(name: str, definition: str) -> None:
    """Appends newly generated framework to MASTER_IP.md."""
    IP_FACTORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(MASTER_FILE, "a", encoding="utf-8") as f:
        f.write(f"- {name} — {definition}\n")


def git_commit(filepath: Path) -> None:
    """Commits created asset to local git tracking using subprocess."""
    try:
        rel_filepath = filepath.relative_to(PROJECT_ROOT)
        rel_master = MASTER_FILE.relative_to(PROJECT_ROOT)
        
        subprocess.run(["git", "add", str(rel_filepath), str(rel_master)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Add new IP framework: {rel_filepath.name}"], 
            check=True
        )
        print(f"[Git] Successfully committed {rel_filepath.name}")
    except Exception as e:
        print(f"[Git Warning] Automated commit skipped: {e}")


# --- Main Engine Loop ---
if __name__ == "__main__":
    print("Starting IP Generator engine with resilient model cascade...")
    
    existing_names = load_existing_ip_names()
    prompt = build_prompt(existing_names)
    raw_ip = generate_ip(prompt)
    
    name, definition = parse_ip(raw_ip)
    filename = save_ip(name, definition)
    update_master_list(name, definition)
    
    git_commit(filename)
    print(f"Successfully generated and processed: {name}")
