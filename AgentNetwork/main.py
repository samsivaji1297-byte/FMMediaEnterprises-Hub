import sys
import os
import json
from pathlib import Path

# Anchor repo root to sys.path so imports across AgentNetwork & MediaFactory work seamlessly
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from AgentNetwork.agents.mindset_agents import SovereignStrategist, KineticScriptwright
from MediaFactory.src.video_builder import build_video
from MediaFactory.src.tts import generate_voiceover  # Import TTS engine

def run_mindset_pipeline(friction_topic: str):
    print("=== [1/3] Sovereign Strategist: Engineering Psychological Hooks ===")
    strategist = SovereignStrategist()
    try:
        strategy = strategist.generate_strategy(friction_topic)
        print(f"[✓] Hook Created: '{strategy.get('hook', 'No hook returned')}'")
    except Exception as e:
        print(f"[!] SovereignStrategist failed: {e}")
        return

    print("\n=== [2/3] Kinetic Scriptwright: Mapping B-Roll & Visual Timing ===")
    scriptwright = KineticScriptwright()
    try:
        blueprint = scriptwright.compile_blueprint(strategy)
        print(f"[✓] Compiled {len(blueprint.get('scenes', []))} kinetic scenes for MediaFactory.")
    except Exception as e:
        print(f"[!] KineticScriptwright failed: {e}")
        return

    print("\n=== [3/3] MediaFactory Engine: Generating Audio & Rendering ===")
    title = blueprint.get("title", "relentless_execution").lower().replace(" ", "_")
    
    # Setup Vault Paths
    vault_dir = REPO_ROOT / "MediaFactory" / "vault"
    renders_dir = vault_dir / "renders"
    audio_dir = vault_dir / "audio"
    
    renders_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Step 3A: Save .txt Caption for Publisher Agent
    caption_text = blueprint.get("caption", f"{title.replace('_', ' ').title()}\n\n#execution #mindset #operator")
    caption_file = renders_dir / f"{title}.txt"
    caption_file.write_text(caption_text, encoding="utf-8")
    print(f"[✓] Caption archived to {caption_file}")

    # Step 3B: Generate Voiceover Audio File
    full_voiceover_text = " ".join([s.get("text", "") for s in blueprint.get("scenes", [])])
    audio_path = audio_dir / f"{title}_audio.mp3"
    
    print(f"[*] Generating TTS Voiceover Audio: {audio_path.name}")
    try:
        generate_voiceover(text=full_voiceover_text, output_path=str(audio_path))
        print(f"[✓] Audio Generated: {audio_path}")
    except Exception as e:
        print(f"[!] Voiceover generation failed: {e}")
        return

    # Step 3C: Render Video via Core Engine
    output_filename = f"{title}.mp4"
    try:
        output_video_path = build_video(
            script_data=blueprint, 
            audio_path=str(audio_path),
            output_filename=output_filename
        )
        print(f"\n[SUCCESS] Render Complete and Saved to Vault: {output_video_path}")
    except Exception as e:
        print(f"[!] Video Rendering failed: {e}")

if __name__ == "__main__":
    default_topic = "wasting time seeking comfort and avoiding hard execution"
    topic = sys.argv[1] if len(sys.argv) > 1 else default_topic
    run_mindset_pipeline(topic)
