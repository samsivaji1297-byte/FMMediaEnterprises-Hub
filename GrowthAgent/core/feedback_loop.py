import sys
import json
import re
from pathlib import Path
from google.genai import types

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import get_client, call_with_fallback

client = get_client()
DB_PATH = SCRIPT_DIR.parent / "data" / "performance_db.json"
PROMPTS_PATH = SCRIPT_DIR.parent / "data" / "active_prompts.json"


def clean_json_text(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def run_self_optimization_cycle():
    """Analyzes performance database and auto-tunes active prompts."""
    if not DB_PATH.exists():
        print("[!] No performance database found. Optimization cycle skipped.")
        return

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[!] Failed to read database ({e}).")
        return

    if len(data) < 2:
        print(f"[*] Data pool too small ({len(data)} entries). Accumulating more data before tuning.")
        return

    # Sort entries by retention score
    sorted_data = sorted(data, key=lambda x: x.get("metrics", {}).get("retention_score", 0), reverse=True)
    top_performers = sorted_data[:3]
    low_performers = sorted_data[-3:]

    prompt = f"""
You are the Autonomous Optimization Engine for a high-retention Instagram Reels agency.
Analyze the performance dataset below and rewrite the agent's active prompt configuration to double conversion.

TOP PERFORMING REELS (Highest Saves/Shares/Retention):
{json.dumps(top_performers, indent=2)}

LOW PERFORMING REELS (High Drop-off/Low Save Rate):
{json.dumps(low_performers, indent=2)}

INSTRUCTIONS:
1. Identify common psychological hooks, text overlay patterns, or narrative mechanics in top performers.
2. Identify failure modes in low performers.
3. Update the `hook_modifier` and `visual_style_modifier` instructions to amplify top-performer mechanics and deprecate weak patterns.

Respond strictly in raw JSON without markdown:
{{
    "system_version": 1.1,
    "winning_patterns": ["Pattern 1", "Pattern 2"],
    "deprecated_hooks": ["Deprecated Hook 1"],
    "hook_modifier": "Refined hook instruction set...",
    "visual_style_modifier": "Refined visual direction..."
}}
"""

    def _api_call_builder(target_model: str):
        def _api_call():
            print(f"[*] Executing Autonomous Prompt Auto-Tuning via: {target_model}")
            gen_config = types.GenerateContentConfig(
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )
            res = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=gen_config
            )
            return res.text.strip()
        return _api_call

    try:
        raw_response = call_with_fallback(_api_call_builder)
        updated_prompts = json.loads(clean_json_text(raw_response))
        
        with open(PROMPTS_PATH, "w", encoding="utf-8") as f:
            json.dump(updated_prompts, f, indent=2)
            
        print("[+] Self-Optimization Cycle Complete. Updated 'data/active_prompts.json'.")
    except Exception as e:
        print(f"[!] Optimization cycle failed ({e}). Prompts remain unchanged.")


if __name__ == "__main__":
    run_self_optimization_cycle()
