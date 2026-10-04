import sys
import inspect
from pathlib import Path
from AgentNetwork.core.schemas import ScriptPayload
from AgentNetwork.config.settings import BASE_DIR, VAULT_DIR

# Ensure MediaFactory root is importable
MEDIAFACTORY_DIR = BASE_DIR / "MediaFactory"
if str(MEDIAFACTORY_DIR) not in sys.path:
    sys.path.append(str(MEDIAFACTORY_DIR))

# Import video_builder module
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

        # Locate build_video or alternative entry point
        target_func = getattr(vb, "build_video", None) or getattr(vb, "build_reel_video", None)

        if not target_func:
            callable_funcs = [
                func for name, func in inspect.getmembers(vb, inspect.isfunction)
                if func.__module__ == vb.__name__
            ]
            if callable_funcs:
                target_func = callable_funcs[0]

        if not target_func:
            raise AttributeError("No callable rendering function found in MediaFactory/src/video_builder.py")

        print(f"[*] Executing rendering via function: '{target_func.__name__}'")

        # Map ScriptPayload fields to the actual parameters expected by build_video()
        sig = inspect.signature(target_func)
        param_names = list(sig.parameters.keys())

        # Candidate mapping dictionary for flexible matching
        payload_map = {
            "hook": script.hook_text,
            "hook_text": script.hook_text,
            "voiceover": script.voiceover_script,
            "voiceover_text": script.voiceover_script,
            "script": script.voiceover_script,
            "audio_text": script.voiceover_script,
            "bullets": script.body_points,
            "body_bullets": script.body_points,
            "body_points": script.body_points,
            "cta": script.call_to_action,
            "cta_text": script.call_to_action,
            "theme": script.theme,
            "visual_keywords": script.visual_search_queries,
            "keywords": script.visual_search_queries,
            "output_path": str(output_path),
            "output_file": str(output_path),
            "filename": str(output_path)
        }

        kwargs = {}
        for param in param_names:
            # Match directly or by keyword fallback
            if param in payload_map:
                kwargs[param] = payload_map[param]
            elif "output" in param or "path" in param:
                kwargs[param] = str(output_path)

        # Call target function using matched parameters or fallback to positional args
        if kwargs:
            rendered_path = target_func(**kwargs)
        else:
            rendered_path = target_func(
                script.hook_text,
                script.voiceover_script,
                script.body_points,
                script.call_to_action,
                script.theme,
                script.visual_search_queries,
                str(output_path)
            )

        final_file = Path(rendered_path if rendered_path else output_path)
        print(f"[✓] Render Complete: {final_file}")
        return final_file
