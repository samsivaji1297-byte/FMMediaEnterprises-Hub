import json
from pathlib import Path
from config import get_client, call_with_fallback
from google.genai import types
from AgentNetwork.core.schemas import SignalPayload, ScriptPayload

# Anchor repo root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

def _load_virality_dossier() -> str:
    """Loads virality guidelines from vault/virality_dossier.md if available."""
    dossier_path = REPO_ROOT / "vault" / "virality_dossier.md"
    if dossier_path.exists():
        try:
            return dossier_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            print(f"[!] Could not read virality dossier in writer.py: {e}")
    return ""


class ScriptEngineAgent:
    def __init__(self):
        self.client = get_client()

    def generate_script(self, signal: SignalPayload) -> ScriptPayload:
        dossier_context = _load_virality_dossier()
        dossier_prompt = f"\nVIRALITY & HOOK FRAMEWORKS TO ENFORCE:\n{dossier_context}\n" if dossier_context else ""

        prompt = f"""
You are a Master Short-Form Video Scriptwriter for Instagram Reels and YouTube Shorts.
Convert this friction signal into a high-retention, fast-paced 15-20 second video script.

SIGNAL DATA:
- Universal Pain Point: {signal.universal_pain_point}
- Search Query Intent: {signal.search_query}
- Initial Hook Seed: {signal.target_hook}
- Actionable Takeaway: {signal.actionable_takeaway}
- Content Pillar: {signal.content_pillar}
{dossier_prompt}
RETENTION RULES:
1. HOOK (0-3s): Punchy, provocative, or pattern-breaking. Max 10 words.
2. VOICEOVER: Spoken script. No intro greetings. Start immediately with the core problem. Max 45 words total.
3. VISUAL BULLETS: 2-3 short text overlays to display during the body.
4. CALL TO ACTION: Single sentence driving saves, shares, or direct comments.
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

        def make_api_call(model_name: str):
            def execute():
                res = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                return res.text
            return execute

        raw_json = ""
        try:
            raw_json = call_with_fallback(make_api_call)
            if raw_json:
                data = json.loads(raw_json)
                return ScriptPayload(
                    title=data.get("title", "relentless_execution"),
                    hook_text=data.get("hook_text", f"Stop wasting hours on {signal.universal_pain_point}."),
                    voiceover_script=data.get("voiceover_script", f"Manual processes are operational leaks. Automate {signal.universal_pain_point} now."),
                    body_points=data.get("body_points", ["Identify manual bottleneck", "Deploy automated trigger"]),
                    call_to_action=data.get("call_to_action", "Comment 'PIPELINE' to deploy the framework."),
                    theme=data.get("theme", "kinetic"),
                    visual_search_queries=data.get("visual_search_queries", ["technology server core", "dark code matrix"])
                )
        except Exception as e:
            print(f"[!] ScriptEngineAgent parsing / execution error: {e}")

        # Safe Fallback ScriptPayload
        return ScriptPayload(
            title="relentless_execution",
            hook_text=f"Stop wasting hours on {signal.universal_pain_point}.",
            voiceover_script=f"Manual processes are operational leaks. Eliminate {signal.universal_pain_point} and scale execution.",
            body_points=["Isolate manual toil", "Execute automated flow"],
            call_to_action="Comment 'PIPELINE' now to get the complete workflow.",
            theme="kinetic",
            visual_search_queries=["dark tech network", "cyberpunk code terminal"]
        )
