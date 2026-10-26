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
MASTER_LAB2_FILE = IP_LAB_2_DIR / "!MASTER_IP.md"

client = get_client()

# --- Expanded Evergreen Human Demand Matrix ---
EVERGREEN_DEMAND_MATRIX = [
    {
        "category": "Wealth Generation & Capital Accumulation",
        "focus": "High-margin asset engines, leverage, capital efficiency, financial sovereignty, automated revenue"
    },
    {
        "category": "Sovereign Career & Professional Dominance",
        "focus": "Unfair career velocity, corporate decoupling, negotiation leverage, executive authority, high-value skill monetization"
    },
    {
        "category": "Execution Velocity & Deep Productivity",
        "focus": "Friction elimination, deep focus state preservation, zero-overhead execution, automated systems, operational leverage"
    },
    {
        "category": "Psychological Fortitude & Unshakeable Confidence",
        "focus": "Internal state control, rejection immunity, resilience under pressure, conviction engineering, cognitive grit"
    },
    {
        "category": "Mental Sovereignty & Cognitive Territory",
        "focus": "Autonomy from external noise, radical self-reliance, strategic clarity, identity mechanics, internal gravity"
    },
    {
        "category": "Market Positioning & Brand Monopoly",
        "focus": "Category design, radical differentiation, authority anchoring, high-ticket perception, sovereign domain creation"
    }
]


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


def build_prompt(existing_names: list[str], target_demand: dict) -> str:
    """Constructs demand-driven prompt anchored to explicit target vector."""
    existing_list = "\n".join(f"- {name}" for name in existing_names)

    return f"""
Existing IP names across all labs:
{existing_list}

Target Evergreen Demand Vector:
- Category: {target_demand['category']}
- Core Focus: {target_demand['focus']}

Generate ONE new sovereign IP framework that solves or captures this specific human demand while maintaining the user's operational identity philosophy.

Tone balance:
- The IP may be mythic, clinical, psychological, operational, or strategic.
- Do NOT lock into any single tone. Vary naturally.
- The IP should feel distinct from existing IPs.

Format:
<Framework Name>
<One-line definition>

Rules:
- The name must be between 2 to 8 words.
- The definition must be one sentence, explicitly bridging the evergreen human demand vector ({target_demand['category']}) with internal operator mechanics.
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


def save_ip(name: str, definition: str, demand_category: str) -> Path:
    """Saves generated IP into IPLab2 directory with explicit metadata header."""
    IP_LAB_2_DIR.mkdir(parents=True, exist_ok=True)
    
    clean_name = "".join(c if c.isalnum() or c in (" ", "_") else "" for c in name)
    filename = IP_LAB_2_DIR / f"{clean_name.replace(' ', '_')}.md"
    
    content = f"# {name}\n**Demand Vector:** {demand_category}\n\n{definition}\n"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


def update_master_ip(name: str, definition: str, demand_category: str) -> None:
    """Logs the new IP into IPLab2/!MASTER_IP.md with demand tracking."""
    IP_LAB_2_DIR.mkdir(parents=True, exist_ok=True)
    
    if not MASTER_LAB2_FILE.exists():
        with open(MASTER_LAB2_FILE, "w", encoding="utf-8") as f:
            f.write("# IPLab2 Master Index — Demand-Driven Frameworks\n\n")

    entry = f"- **[{demand_category}]** {name} — {definition}\n"
    with open(MASTER_LAB2_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


def git_commit(filepath: Path) -> None:
    """Commits created asset and updated master index to git tracking."""
    try:
        rel_filepath = filepath.relative_to(PROJECT_ROOT)
        rel_master = MASTER_LAB2_FILE.relative_to(PROJECT_ROOT)
        
        subprocess.run(["git", "add", str(rel_filepath), str(rel_master)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Add demand-driven IP to IPLab2: {rel_filepath.name}"], 
            check=True
        )
        print(f"[Git] Successfully committed {rel_filepath.name} and !MASTER_IP.md")
    except Exception as e:
        print(f"[Git Warning] Automated commit skipped: {e}")


# --- Main Engine Loop ---
if __name__ == "__main__":
    print("Starting Demand-Driven IP Generator for IPLab2...")
    
    existing_names = load_existing_ip_names()
    target_demand = random.choice(EVERGREEN_DEMAND_MATRIX)
    
    print(f"Targeting Demand Vector: {target_demand['category']}")
    
    prompt = build_prompt(existing_names, target_demand)
    raw_ip = generate_ip(prompt)
    
    name, definition = parse_ip(raw_ip)
    filename = save_ip(name, definition, target_demand['category'])
    update_master_ip(name, definition, target_demand['category'])
    
    git_commit(filename)
    print(f"Successfully generated demand-driven IP: {name}")
