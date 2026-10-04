import sys
import asyncio
from pathlib import Path
import edge_tts
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
        self.audio_dir = VAULT_DIR / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def _generate_tts_audio(self, text: str, output_path: Path) -> Path:
        """Generates TTS audio file via edge-tts."""
        print(f"[*] Generating TTS Voiceover Audio: {output_path.name}")
        
        async def _speak():
            communicate = edge_tts.Communicate(text, voice="en-US-ChristopherNeural")
            await communicate.save(str(output_path))

        asyncio.run(_speak())
        print(f"[✓] Audio Generated: {output_path}")
        return output_path

    def render_script(self, script: ScriptPayload) -> Path:
        """Passes script payload and generated audio directly into MediaFactory rendering pipeline."""
        slug = script.title.lower().replace(' ', '_').replace('?', '').replace("'", '')
        output_video_path = self.output_dir / f"{slug}.mp4"
        output_audio_path = self.audio_dir / f"{slug}_audio.mp3"

        print(f"[*] Dispatching to MediaFactory Engine: {script.title}")

        # Step 1: Generate Voiceover Audio
        self._generate_tts_audio(script.voiceover_script, output_audio_path)

        target_func = getattr(vb, "build_video", None) or getattr(vb, "build_reel_video", None)

        if not target_func:
            raise AttributeError("No callable rendering function found in MediaFactory/src/video_builder.py")

        # Step 2: Construct Script Data Dictionary
        script_dict = {
            "title": script.title,
            "hook_text": script.hook_text,
            "voiceover_script": script.voiceover_script,
            "body_points": script.body_points,
            "call_to_action": script.call_to_action,
            "theme": script.theme,
            "visual_search_queries": script.visual_search_queries,
            "output_path": str(output_video_path)
        }

        print(f"[*] Executing rendering via '{target_func.__name__}' with script_data & audio_path")

        # Step 3: Call build_video with required script_data and audio_path positional arguments
        rendered_path = target_func(script_dict, str(output_audio_path))

        final_file = Path(rendered_path if rendered_path else output_video_path)
        print(f"[✓] Render Complete: {final_file}")
        return final_file
