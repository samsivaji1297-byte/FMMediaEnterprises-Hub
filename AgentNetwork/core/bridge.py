import sys
from pathlib import Path
from AgentNetwork.core.schemas import ScriptPayload
from AgentNetwork.config.settings import BASE_DIR, VAULT_DIR

# Ensure MediaFactory root is importable
MEDIAFACTORY_DIR = BASE_DIR / "MediaFactory"
if str(MEDIAFACTORY_DIR) not in sys.path:
    sys.path.append(str(MEDIAFACTORY_DIR))

# Import MediaFactory execution functions
from src.video_builder import build_reel_video

class MediaFactoryBridge:
    def __init__(self):
        self.output_dir = VAULT_DIR / "renders"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_script(self, script: ScriptPayload) -> Path:
        """Passes script payload directly into MediaFactory rendering pipeline."""
        output_filename = f"{script.title.lower().replace(' ', '_')}.mp4"
        output_path = self.output_dir / output_filename

        print(f"[*] Dispatching to MediaFactory Engine: {script.title}")
        
        # Executes video compositing using the refactored MoviePy v2 module
        rendered_path = build_reel_video(
            hook_text=script.hook_text,
            voiceover_text=script.voiceover_script,
            body_bullets=script.body_points,
            cta_text=script.call_to_action,
            theme=script.theme,
            visual_keywords=script.visual_search_queries,
            output_path=str(output_path)
        )

        print(f"[✓] Render Complete: {rendered_path}")
        return Path(rendered_path)
