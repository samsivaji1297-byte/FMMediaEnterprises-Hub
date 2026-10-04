import json
from config import get_client, call_with_fallback
from google.genai import types
from AgentNetwork.core.schemas import SignalPayload, ScriptPayload

class ScriptEngineAgent:
    def __init__(self):
        self.client = get_client()

    def generate_script(self, signal: SignalPayload) -> ScriptPayload:
        prompt = f"""
        You are a Master Short-Form Video Scriptwriter for Instagram Reels and YouTube Shorts.
        Convert this friction signal into a high-retention, fast-paced 15-20 second video script.

        SIGNAL DATA:
        - Universal Pain Point: {signal.universal_pain_point}
        - Search Query Intent: {signal.search_query}
        - Initial Hook Seed: {signal.target_hook}
        - Actionable Takeaway: {signal.actionable_takeaway}
        - Content Pillar: {signal.content_pillar}

        RETENTION RULES:
        1. HOOK (0-3s): Punchy, provocative, or pattern-breaking. Max 10 words.
        2. VOICEOVER: Spoken script. No fluff or fluff introductions. Start immediately with the core problem. Max 45 words total.
        3. VISUAL BULLETS: 2-3 short text overlays to display during the body.
        4. CALL TO ACTION: Single sentence driving saves or shares.
        5. THEME: Select one of ['sovereign', 'ambient', 'kinetic'].

        Return JSON matching this schema:
        {{
            "title": "str",
            "hook_text": "str",
            "voiceover_script": "str",
            "body_points": ["str", "str"],
            "call_to_action": "str",
            "theme": "sovereign|ambient|kinetic",
            "visual_search_queries": ["str", "str"]
        }}
        """

        def api_call(model_name: str):
            res = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return res.text

        raw_json = call_with_fallback(api_call)
        data = json.loads(raw_json)

        return ScriptPayload(
            title=data["title"],
            hook_text=data["hook_text"],
            voiceover_script=data["voiceover_script"],
            body_points=data["body_points"],
            call_to_action=data["call_to_action"],
            theme=data["theme"],
            visual_search_queries=data["visual_search_queries"]
        )
