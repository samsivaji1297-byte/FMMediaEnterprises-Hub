import sys
import inspect
from pathlib import Path
from AgentNetwork.core.schemas import ScriptPayload
from AgentNetwork.config.settings import BASE_DIR, VAULT_DIR

# Ensure MediaFactory root is importable
MEDIAFACTORY_DIR = BASE_DIR / "MediaFactory"
if str(MEDIAFACTORY_DIR) not in sys.path:
    sys.path.append(str(MEDIAFACTORY_DIR))

import src.video_builder as vb

class MediaFactoryBridge:
    def __init__(self):
        self.output_dir = VAULT_DIR / "renders"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_script(self, script: ScriptPayload) -> Path:
        """Passes script payload directly into MediaFactory rendering pipeline."""
        output_filename = f"{script.title.lower().replace(' ', '_')}.mp4"
        output_path = self.output_dir / output_filename

        print(f"[*] Dispatching to MediaFactory Engine: {script.title}")

        target_func = getattr(vb, "build_video", None) or getattr(vb, "build_reel_video", None)

        if not target_func:
            raise AttributeError("No callable rendering function found in MediaFactory/src/video_builder.py")

        # Convert Pydantic payload to dictionary expected by MediaFactory
        script_dict = {
            "title": script.title,
            "hook_text": script.hook_text,
            "voiceover_script": script.voiceover_script,
            "body_points": script.body_points,
            "call_to_action": script.call_to_action,
            "theme": script.theme,
            "visual_search_queries": script.visual_search_queries,
            "output_path": str(output_path)
        }

        print(f"[*] Executing rendering via function: '{target_func.__name__}' with script_data dictionary")

        # Call build_video passing script_data dictionary
        rendered_path = target_func(script_data=script_dict)

        final_file = Path(rendered_path if rendered_path else output_path)
        print(f"[✓] Render Complete: {final_file}")
        return final_file
