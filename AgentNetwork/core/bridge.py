import sys
import inspect
from pathlib import Path
from AgentNetwork.core.schemas import ScriptPayload
from AgentNetwork.config.settings import BASE_DIR, VAULT_DIR

# Ensure MediaFactory root is importable
MEDIAFACTORY_DIR = BASE_DIR / "MediaFactory"
if str(MEDIAFACTORY_DIR) not in sys.path:
    sys.path.append(str(MEDIAFACTORY_DIR))

# Import video_builder module dynamically
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
        
        # Discover top-level functions defined in video_builder
        callable_funcs = {
            name: func for name, func in inspect.getmembers(vb, inspect.isfunction)
            if func.__module__ == vb.__name__
        }

        # Look for explicit name matches first, fallback to the first available function
        target_func = (
            callable_funcs.get("build_reel_video") or
            callable_funcs.get("generate_reel") or
            callable_funcs.get("create_video") or
            callable_funcs.get("build_video") or
            callable_funcs.get("render_video") or
            callable_funcs.get("main")
        )

        if not target_func and callable_funcs:
            # Fall back to the primary function defined in video_builder.py
            target_func = list(callable_funcs.values())[0]

        if not target_func:
            raise AttributeError(
                f"No callable rendering function found in MediaFactory/src/video_builder.py. "
                f"Available attributes: {dir(vb)}"
            )

        print(f"[*] Executing rendering via function: '{target_func.__name__}'")

        # Execute render call with script payload kwargs
        rendered_path = target_func(
            hook_text=script.hook_text,
            voiceover_text=script.voiceover_script,
            body_bullets=script.body_points,
            cta_text=script.call_to_action,
            theme=script.theme,
            visual_keywords=script.visual_search_queries,
            output_path=str(output_path)
        )

        final_file = Path(rendered_path if rendered_path else output_path)
        print(f"[✓] Render Complete: {final_file}")
        return final_file
