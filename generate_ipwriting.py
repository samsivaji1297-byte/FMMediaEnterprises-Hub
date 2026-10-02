import sys
import random
import datetime
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo
from google.genai import types

# Resolve project root path for clean config imports
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import get_client, call_with_fallback

# --- Configuration & Directories ---
IP_DIR = PROJECT_ROOT / "IPFactory"
OUTPUT_DIR = PROJECT_ROOT / "WritingFactory" / "IPDriven"

client = get_client()


def load_ips() -> list[str]:
    """Scans IPFactory for valid IP framework Markdown files."""
    if not IP_DIR.exists():
        return []

    ips = []
    for filepath in IP_DIR.glob("*.md"):
        if filepath.name == "!MASTER_IP.md":
            continue
        
        with open(filepath, "r", encoding="utf-8") as f:
            header = f.readline().strip()
            if header.startswith("# "):
                ips.append(header[2:].strip())
    return ips


def build_prompt(ip_name: str) -> str:
    """Constructs prompt for IP expansion writing."""
    return f"""
Write 300–400 words expanding the following sovereign IP framework:

{ip_name}

Constraints:
- Blend mythic, clinical, psychological, operational, and strategic tones.
- Must align with: Mental Sovereignty, Identity Mechanics, Operator Autonomy, Empire Architecture.
- Produce structured writing with natural paragraph flow.
- Break the writing into 3–5 paragraphs.
- Insert a blank line between each paragraph.
- No headings.
- No bullet points.
- No lists.
- No formatting.
"""


def generate_ip_writing(ip_name: str) -> str:
    """Executes prompt against model cascade with disabled automatic function calling warnings."""
    prompt = build_prompt(ip_name)

    def _api_func_builder(target_model: str):
        def _api_call():
            print(f"Requesting IP writing expansion using model: {target_model}")
            
            # Suppress SDK warning logs
            gen_config = types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )
            
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=gen_config,
            )
            
            text = response.text.strip()
            # Normalize multiple newlines to clean double paragraph breaks
            paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
            return "\n\n".join(paragraphs)

        return _api_call

    return call_with_fallback(_api_func_builder)


def save_output(ip_name: str, text: str) -> Path:
    """Saves generated expansion into WritingFactory/IPDriven with Sydney timestamp."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Local Sydney timestamp
    timestamp = datetime.datetime.now(ZoneInfo("Australia/Sydney")).strftime("%Y-%m-%d_%H-%M-%S")
    clean_name = "".join(c if c.isalnum() or c in (" ", "_") else "" for c in ip_name)
    safe_name = clean_name.replace(" ", "_")
    
    filepath = OUTPUT_DIR / f"{safe_name}_{timestamp}.md"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {ip_name} — Writing Expansion\n\n{text}\n")

    print(f"Saved IP-driven writing: {filepath}")
    return filepath


def git_commit(filepath: Path) -> None:
    """Commits created writing asset to local Git tracking using subprocess."""
    try:
        rel_filepath = filepath.relative_to(PROJECT_ROOT)
        
        subprocess.run(["git", "add", str(rel_filepath)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Add IP writing expansion: {rel_filepath.name}"], 
            check=True
        )
        print(f"[Git] Successfully committed {rel_filepath.name}")
    except Exception as e:
        print(f"[Git Warning] Automated commit skipped: {e}")


def main():
    print("Starting IP Writing Expansion Engine...")
    
    ips = load_ips()
    if not ips:
        raise RuntimeError("No valid IP frameworks found in IPFactory.")

    selected_ip = random.choice(ips)
    print(f"Selected Framework: {selected_ip}")

    writing_text = generate_ip_writing(selected_ip)
    saved_filepath = save_output(selected_ip, writing_text)
    
    git_commit(saved_filepath)


if __name__ == "__main__":
    main()
