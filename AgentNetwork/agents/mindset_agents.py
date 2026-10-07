import os
import json
from pathlib import Path
import google.generativeai as genai

# Model cascade hierarchy (Primary -> Fallbacks)
MODEL_CASCADE = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash"
]

class GeminiCascadeClient:
    """Handles multi-model fallback execution for Google Gemini API."""
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def generate_with_fallback(self, prompt: str) -> str:
        if not self.api_key:
            print("[!] GEMINI_API_KEY missing. Falling back to offline template.")
            return ""

        for model_name in MODEL_CASCADE:
            try:
                print(f"[*] Dispatching prompt to model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    print(f"[✓] Generation successful using {model_name}")
                    return response.text
            except Exception as e:
                print(f"[!] Warning: {model_name} failed ({e}). Cascading to next model...")

        print("[!] All models in cascade failed. Utilizing offline fallback payload.")
        return ""


class SovereignStrategist:
    """Generates direct-response narrative angles and ruthless hooks."""
    def __init__(self):
        self.client = GeminiCascadeClient()

    def generate_strategy(self, friction_point: str) -> dict:
        prompt = (
            f"You are the SovereignStrategist for an aggressive direct-response media engine.\n"
            f"Friction point to target: '{friction_point}'\n\n"
            f"Provide a strict JSON object with these keys:\n"
            f"- 'hook': Relentless, high-friction opening line\n"
            f"- 'core_message': Concise direct-response pitch\n"
            f"- 'call_to_action': Explicit, urgent command to act\n"
            f"Respond with JSON ONLY. No markdown, no prose."
        )

        raw_response = self.client.generate_with_fallback(prompt)
        
        if raw_response:
            try:
                cleaned = raw_response.strip().replace("```json", "").replace("```", "")
                return json.loads(cleaned)
            except Exception as e:
                print(f"[!] JSON parsing error from SovereignStrategist: {e}")

        # Standard Offline Fallback
        return {
            "hook": f"Stop wasting hours on {friction_point}.",
            "core_message": "Manual work is operational failure. Automate your execution or get left behind.",
            "call_to_action": "Comment 'PIPELINE' now to deploy the war room framework."
        }


class KineticScriptwright:
    """Formats strategy into kinetic scene breakdowns and visual parameters."""
    def __init__(self):
        self.client = GeminiCascadeClient()

    def compile_blueprint(self, strategy: dict) -> dict:
        hook = strategy.get("hook", "Eliminate manual friction.")
        message = strategy.get("core_message", "Deploy autonomous architecture.")
        cta = strategy.get("call_to_action", "Comment PIPELINE.")

        prompt = (
            f"Format this content into a kinetic 3-scene video blueprint:\n"
            f"Hook: {hook}\nMessage: {message}\nCTA: {cta}\n\n"
            f"Provide a strict JSON object with:\n"
            f"- 'title': snake_case_identifier\n"
            f"- 'caption': Instagram caption text with relevant hashtags\n"
            f"- 'scenes': Array of 3 objects, each with 'scene_id', 'text', and 'visual_prompt'\n"
            f"Respond with JSON ONLY."
        )

        raw_response = self.client.generate_with_fallback(prompt)

        if raw_response:
            try:
                cleaned = raw_response.strip().replace("```json", "").replace("```", "")
                return json.loads(cleaned)
            except Exception as e:
                print(f"[!] JSON parsing error from KineticScriptwright: {e}")

        # Standard Offline Blueprint Fallback
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
