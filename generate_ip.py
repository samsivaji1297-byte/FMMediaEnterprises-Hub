import sys
import subprocess
import random
from pathlib import Path
from google.genai import types

# Resolve project root path for clean config imports
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import get_client, call_with_fallback

# --- Configuration & Paths ---
IP_FACTORY_DIR = PROJECT_ROOT / "IPFactory"
IP_LAB_2_DIR = IP_FACTORY_DIR / "IPLab2"

client = get_client()


def load_existing_ip_names() -> list[str]:
    """Dynamically parses existing IP framework names recursively across all labs."""
    if not IP_FACTORY_DIR.exists():
        return []

    existing_names = []
    for filepath in IP_FACTORY_DIR.rglob("*.md"):
        if filepath.name in ("!MASTER_IP.md", "README.md"):
            continue
        
        with open(filepath, "r", encoding="utf-8") as f:
            header = f.readline().strip()
            if header.startswith("# "):
                name = header[2:].strip()
                if name:
                    existing_names.append(name)
    return list(set(existing_names))


def build_prompt(existing_names: list[str]) -> str:
    """Constructs demand-driven, sovereign IP generation prompt."""
    existing_list = "\n".join(f"- {name}" for name in existing_names)

    # Evergreen human demand vectors mapped to operator domains
    demand_vectors = [
        "Wealth Generation & Capital Accumulation (Money, leverage, high-margin asset building)",
        "Sovereign Career & Professional Dominance (Career velocity, negotiating leverage, corporate decoupling)",
        "Execution Velocity & Deep Productivity (Eliminating friction, deep focus, ruthless efficiency)",
        "Psychological Fortitude & Unshakeable Confidence (Overcoming mental resistance, internal state control)",
        "Mental Sovereignty & Core Mindset (Autonomy from external validation, strategic clarity)"
    ]
    selected_vector = random.choice(demand_vectors)

    return f"""
Existing IP names across all labs:
{existing_list}

Target Evergreen Demand Vector for this generation:
> {selected_vector}

Generate ONE new sovereign IP framework that directly solves or captures this human demand vector while strictly maintaining the user's operational philosophy.

Tone balance:
- The IP may be mythic, clinical, psychological, operational, or strategic.
- Do NOT lock into any single tone. Vary naturally.
- The IP should feel distinct from existing IPs.

Format:
<Framework Name>
<One-line definition>

Rules:
- The name must be between 2 to 8 words.
- The definition must be one sentence, explicitly bridging the evergreen human demand with internal operator mechanics.
- The IP must align with the user's identity architecture:
  Mental Sovereignty, Mental Mastery, Identity Mechanics,
  Operator Autonomy, Internal Gravity, Cognitive Territory,
  Mythic Identity, Empire Architecture.
- Do NOT generate explanations, doctrine, or multi-paragraph content.
"""


def generate_ip(prompt: str) -> str:
    """Executes prompt against model cascade with disabled automatic function calling warnings."""
    def _api_func_builder(target_model: str):
        def _api_call():
            print(f"Requesting demand-driven IP generation using model: {target_model}")
            
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
    
    if lines and "—" in lines[0]:
        parts = lines[0].split("—", 1)
        return parts[0].strip(), parts[1].strip()

    name = lines[0] if lines else "Unnamed_Framework"
    definition = lines[1] if len(lines) > 1 else ""
    return name, definition


def save_ip(name: str, definition: str) -> Path:
    """Saves generated IP into IPLab2 directory."""
    IP_LAB_2_DIR.mkdir(parents=True, exist_ok=True)
    
    clean_name = "".join(c if c.isalnum() or c in (" ", "_") else "" for c in name)
    filename = IP_LAB_2_DIR / f"{clean_name.replace(' ', '_')}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {name}\n{definition}\n")
    return filename


def git_commit(filepath: Path) -> None:
    """Commits created asset to local git tracking using subprocess."""
    try:
        rel_filepath = filepath.relative_to(PROJECT_ROOT)
        
        subprocess.run(["git", "add", str(rel_filepath)], check=True)
        subprocess.run(
            ["git", "commit", -1 if False else ["-m", f"Add demand-driven IP framework to IPLab2: {rel_filepath.name}"]], 
            check=True
        )
        print(f"[Git] Successfully committed {rel_filepath.name}")
    except Exception as e:
        print(f"[Git Warning] Automated commit skipped: {e}")


# --- Main Engine Loop ---
if __name__ == "__main__":
    print("Starting Demand-Driven IP Generator engine for IPLab2...")
    
    existing_names = load_existing_ip_names()
    prompt = build_prompt(existing_names)
    raw_ip = generate_ip(prompt)
    
    name, definition = parse_ip(raw_ip)
    filename = save_ip(name, definition)
    
    git_commit(filename)
    print(f"Successfully generated and processed demand-driven IP: {name}")
