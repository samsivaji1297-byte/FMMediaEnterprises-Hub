import sys
import subprocess
from pathlib import Path
from google.genai import types

# Resolve project root path for clean config imports
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import get_client, call_with_fallback

# --- Configuration & Directories ---
IP_DIR = PROJECT_ROOT / "IPFactory"
MASTER_FILE = IP_DIR / "!MASTER_IP.md"

client = get_client()


def load_master_lines() -> list[str]:
    """Loads lines from !MASTER_IP.md if it exists."""
    if not MASTER_FILE.exists():
        return []
    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        return f.readlines()


def save_master_lines(lines: list[str]) -> None:
    """Saves updated lines back to !MASTER_IP.md."""
    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)


def build_prompt(name: str) -> str:
    """Constructs prompt for repair definition generation."""
    return f"""
Generate a one-sentence definition for the following sovereign IP framework name:

{name}

Constraints:
- One sentence only.
- Tone may be mythic, clinical, psychological, operational, or strategic.
- Must align with: Mental Sovereignty, Mental Mastery, Identity Mechanics,
  Operator Autonomy, Internal Gravity, Cognitive Territory, Mythic Identity, Empire Architecture.
- No extra commentary, no headings, no bullet points. Just the sentence.
"""


def generate_definition(name: str) -> str:
    """Executes prompt against model cascade with disabled automatic function calling warnings."""
    prompt = build_prompt(name)

    def _api_func_builder(target_model: str):
        def _api_call():
            print(f"Generating repair definition for '{name}' using model: {target_model}")
            
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
            # Ensure it's strictly a single line
            return " ".join(text.splitlines()).strip()

        return _api_call

    return call_with_fallback(_api_func_builder)


def repair_ip_file(filepath: Path) -> str | None:
    """Checks and repairs an individual IP Markdown file. Returns definition if repaired, else None."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return None

    # Format expected: line 0 -> "# Name", line 1 -> definition
    header = lines[0].strip()
    if not header.startswith("# "):
        return None

    name = header[2:].strip()

    # If second line already contains a non-empty definition, skip repair
    if len(lines) > 1 and lines[1].strip():
        return None

    # Generate definition to repair incomplete file
    definition = generate_definition(name)
    if len(lines) > 1:
        lines[1] = definition + "\n"
    else:
        lines.append(definition + "\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Repaired definition for file: {filepath.name}")
    return definition


def repair_master_entry(master_lines: list[str], name: str, definition: str) -> bool:
    """Updates matching entry in !MASTER_IP.md lines."""
    updated = False
    for i, line in enumerate(master_lines):
        stripped = line.strip()
        if stripped.startswith("- "):
            content = stripped[2:]
            if content.startswith(name):
                master_lines[i] = f"- {name} — {definition}\n"
                updated = True
                break
    if updated:
        print(f"Updated master entry for: {name}")
    return updated


def git_commit_repairs(repaired_files: list[Path]) -> None:
    """Commits all repaired IP files to Git tracking in one batch."""
    if not repaired_files:
        return

    try:
        rel_paths = [str(f.relative_to(PROJECT_ROOT)) for f in repaired_files]
        subprocess.run(["git", "add"] + rel_paths, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Repair IP integrity across {len(repaired_files)} file(s)"],
            check=True,
        )
        print(f"[Git] Successfully committed repairs for {len(repaired_files)} file(s)")
    except Exception as e:
        print(f"[Git Warning] Automated commit skipped: {e}")


def main():
    print("Starting IP Integrity Repair Engine...")
    
    if not IP_DIR.exists():
        print("IPFactory directory does not exist. Nothing to repair.")
        return

    master_lines = load_master_lines()
    changed_master = False
    repaired_files: list[Path] = []

    for filepath in IP_DIR.glob("*.md"):
        if filepath.name == "!MASTER_IP.md":
            continue

        definition = repair_ip_file(filepath)
        if definition:
            repaired_files.append(filepath)
            
            # Extract name from header to sync master index
            with open(filepath, "r", encoding="utf-8") as f:
                header = f.readline().strip()
            name = header[2:].strip()

            if repair_master_entry(master_lines, name, definition):
                changed_master = True

    if changed_master:
        save_master_lines(master_lines)
        repaired_files.append(MASTER_FILE)
        
    if repaired_files:
        git_commit_repairs(repaired_files)
    else:
        print("All IP frameworks intact. No repairs needed.")


if __name__ == "__main__":
    main()
