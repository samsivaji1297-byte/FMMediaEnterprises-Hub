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
from GrowthAgent.core.friction_bank import get_friction_vector

client = get_client()
PROMPTS_PATH = SCRIPT_DIR.parent / "data" / "active_prompts.json"


def load_active_prompts() -> dict:
    if PROMPTS_PATH.exists():
        try:
            with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"hook_modifier": "Focus on high-stakes pattern interrupts.", "visual_style_modifier": "Dark charcoal minimalist."}


def clean_json_text(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def generate_psychology_reel(product_key: str = None) -> dict:
    """Generates a high-retention 3-scene vertical script aligned with Gumroad product conversion."""
    vector = get_friction_vector(product_key)
    prompts = load_active_prompts()

    prompt = f"""
You are an elite Instagram Reels content strategist and human behavior psychologist.
Synthesize a high-retention 15-20 second vertical Reel script targeting human friction.

PRODUCT CONVERSION TARGET:
- Product: {vector['product_name']}
- Core Pain: {vector['core_pain']}
- Target Desire: {vector['target_desire']}
- Hook Anchor: "{vector['selected_hook_angle']}"

STRATEGY MODIFIERS (Auto-Tuned by Growth Agent):
- Hook Strategy: {prompts.get('hook_modifier', '')}
- Visual Direction: {prompts.get('visual_style_modifier', '')}

CRITICAL STRUCTURAL RULES:
1. EXACTLY 3 scenes.
2. Scene 1 MUST be a 1.5-second visual and auditory pattern interrupt.
3. Scene 2 MUST deliver high-density reframe/solution.
4. Scene 3 MUST drive a high-converting comment-trigger CTA for Gumroad access.

Output strictly in raw JSON without markdown formatting:
{{
    "title": "Short internal title",
    "product_key": "{vector['product_key']}",
    "voiceover_full": "Concatenated full narration",
    "caption": "Full Instagram post caption with CTA",
    "scenes": [
        {{
            "scene_id": 1,
            "duration_seconds": 3,
            "narration": "First 3-5 words pattern interrupt",
            "text_overlay": "2-4 WORDS MAX IMPACT",
            "visual_prompt": "Cinematic vertical 9:16 high-contrast aesthetic description"
        }},
        {{
            "scene_id": 2,
            "duration_seconds": 8,
            "narration": "Core reframe and solution mechanism",
            "text_overlay": "KEY INSIGHT PHRASE",
            "visual_prompt": "Cinematic vertical 9:16 high-contrast aesthetic description"
        }},
        {{
            "scene_id": 3,
            "duration_seconds": 4,
            "narration": "Comment CTA prompt for protocol",
            "text_overlay": "COMMENT '{vector['cta_keyword'].upper()}' BELOW",
            "visual_prompt": "Cinematic vertical 9:16 minimalist CTA aesthetic"
        }}
    ]
}}
"""

    def _api_call_builder(target_model: str):
        def _api_call():
            print(f"[*] Synthesizing Reel script with model: {target_model}")
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

    raw_response = call_with_fallback(_api_call_builder)
    return json.loads(clean_json_text(raw_response))


if __name__ == "__main__":
    print("[*] Generating Test Reel Script...")
    script = generate_psychology_reel("OPERATOR_MINDSET_KIT")
    print(json.dumps(script, indent=2))
