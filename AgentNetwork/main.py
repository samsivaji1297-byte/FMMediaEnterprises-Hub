import sys
from pathlib import Path
from AgentNetwork.agents.mindset_agents import SovereignStrategist, KineticScriptwright
from MediaFactory.src.video_builder import build_video

def run_mindset_pipeline(friction_topic: str):
    print(f"=== [1/3] Sovereign Strategist: Engineering Psychological Hooks ===")
    strategist = SovereignStrategist()
    strategy = strategist.generate_strategy(friction_topic)
    print(f"[✓] Hook Created: '{strategy.get('hook')}'")

    print(f"\n=== [2/3] Kinetic Scriptwright: Mapping B-Roll & Visual Timing ===")
    scriptwright = KineticScriptwright()
    blueprint = scriptwright.compile_blueprint(strategy)
    print(f"[✓] Compiled {len(blueprint.get('scenes', []))} kinetic scenes for MediaFactory.")

    print(f"\n=== [3/3] MediaFactory Engine: Rendering & Archiving ===")
    title = blueprint.get("title", "relentless_execution")
    
    # Save .txt caption alongside the video so Publisher picks it up directly
    renders_dir = Path("MediaFactory/vault/renders")
    renders_dir.mkdir(parents=True, exist_ok=True)
    caption_file = renders_dir / f"{title}.txt"
    caption_file.write_text(blueprint.get("caption", ""), encoding="utf-8")

    # Render video through core pipeline
    output_video_path = build_video(script_data=blueprint, output_filename=f"{title}.mp4")
    print(f"[SUCCESS] Render Complete -> {output_video_path}")

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "wasting time seeking comfort and avoiding hard execution"
    run_mindset_pipeline(topic)
