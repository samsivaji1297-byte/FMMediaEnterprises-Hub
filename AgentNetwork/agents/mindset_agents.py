import sys
import json
from pathlib import Path
from google.genai import types

# Anchor repo root to sys.path for config import
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from config import get_client, call_with_fallback

client = get_client()


def _generate_with_cascade(prompt: str) -> str:
    """Dispatches prompt through the central model cascade configured in config.py."""
    def _api_func_builder(target_model: str):
        def _api_call():
            print(f"[*] Requesting generation using model: {target_model}")
            
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

    try:
        return call_with_fallback(_api_func_builder)
    except Exception as e:
        print(f"[!] Cascade execution failed: {e}")
        return ""


class SovereignStrategist:
    """Generates direct-response narrative angles and ruthless hooks."""

    def generate_strategy(self, friction_point: str) -> dict:
        prompt = f"""
You are the SovereignStrategist for an aggressive direct-response media engine.
Friction point to target: '{friction_point}'

Provide a strict JSON object with these exact keys:
- "hook": Relentless, high-friction opening line
- "core_message": Concise direct-response pitch
- "call_to_action": Explicit, urgent command to act

Rules:
- Respond with JSON ONLY.
- Do NOT include markdown code fences (```json), explanations, or surrounding text.
"""
        raw_response = _generate_with_cascade(prompt)

        if raw_response:
            try:
                cleaned = raw_response.strip().replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned)
            except Exception as e:
                print(f"[!] SovereignStrategist JSON parse error: {e}")

        # Offline Fallback Payload
        return {
            "hook": f"Stop wasting hours on {friction_point}.",
            "core_message": "Manual work is operational failure. Automate your execution or get left behind.",
            "call_to_action": "Comment 'PIPELINE' now to deploy the war room framework."
        }


class KineticScriptwright:
    """Formats strategy into kinetic scene breakdowns and visual parameters."""

    def compile_blueprint(self, strategy: dict) -> dict:
        hook = strategy.get("hook", "Eliminate manual friction.")
        message = strategy.get("core_message", "Deploy autonomous architecture.")
        cta = strategy.get("call_to_action", "Comment PIPELINE.")

        prompt = f"""
Format this direct-response concept into a 3-scene video blueprint:
Hook: {hook}
Message: {message}
CTA: {cta}

Provide a strict JSON object with these exact keys:
- "title": snake_case_identifier
- "caption": Instagram caption text with hashtags
- "scenes": Array of 3 objects, each with "scene_id", "text", and "visual_prompt"

Rules:
- Respond with JSON ONLY.
- Do NOT include markdown code fences (```json), explanations, or surrounding text.
"""
        raw_response = _generate_with_cascade(prompt)

        if raw_response:
            try:
                cleaned = raw_response.strip().replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned)
            except Exception as e:
                print(f"[!] KineticScriptwright JSON parse error: {e}")

        # Offline Blueprint Fallback
        slug_title = "".join(c for c in hook[:20] if c.isalnum() or c == " ").strip().replace(" ", "_").lower()
        return {
            "title": slug_title or "relentless_execution",
            "caption": f"{hook}\n\n{message}\n\n{cta}\n\n#execution #automation #mindset #operator",
            "scenes": [
                {"scene_id": 1, "text": hook, "visual_prompt": "Dark charcoal dashboard with glowing cyan data feeds"},
                {"scene_id": 2, "text": message, "visual_prompt": "High-contrast terminal output scrolling execution logs"},
                {"scene_id": 3, "text": cta, "visual_prompt": "Bold gold text overlay on obsidian background"}
            ]
        }
