import os
import re
import json
import random
import shutil
import argparse
from datetime import datetime
from script_generator import generate_reel_content
from audio_generator import create_audio
from video_builder import build_video

# Sovereign Identity & High-Signal Topic Pool
TOPIC_POOL = [
    "Identity & Self-Mastery",
    "Ruthless Time Reclamation",
    "Sovereign Execution",
    "Signal Over Noise",
    "The Sovereign Operator Mindset",
    "Silence as Strategic Leverage",
    "Building Systems Over Dreams"
]

THEME_POOL = ["sovereign", "ambient", "kinetic"]

def slugify(text: str) -> str:
    """Converts a topic string into a clean filename slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text)

def run_pipeline(topic: str = None, theme: str = None):
    # 1. Dynamic Topic & Theme Resolution
    if not topic or topic.strip() == "":
        topic = random.choice(TOPIC_POOL)
        print(f"[AUTO-SELECT] Selected Topic from Identity Pool: '{topic}'")
        
    if not theme or theme.strip() == "":
        theme = random.choice(THEME_POOL)
        print(f"[AUTO-SELECT] Selected Design Theme: '{theme.upper()}'")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    topic_slug = slugify(topic)
    run_id = f"{timestamp}_{topic_slug}"
    
    print(f"=== Initiating MediaFactory Engine | Run ID: {run_id} ===")
    
    # 2. Script & Visual Breakdown Generation
    print("[1/4] Generating script & scene breakdown with Gemini...")
    script_data = generate_reel_content(topic)
    
    # 3. Audio Synthesis
    print("[2/4] Synthesizing voiceover track...")
    audio_file = "voice.mp3"
    create_audio(script_data["voiceover_full"], output_path=audio_file)
    
    # 4. Video Composition
    print(f"[3/4] Rendering video composition with [{theme.upper()}] design preset...")
    temp_video = "temp_reel.mp4"
    build_video(script_data, audio_path=audio_file, theme=theme, output_path=temp_video)
    
    # 5. Archive to Repository Vault
    print("[4/4] Vaulting rendered assets to repository...")
    vault_dir = os.path.join("..", "vault", run_id)
    os.makedirs(vault_dir, exist_ok=True)
    
    final_video_name = f"reel_{run_id}.mp4"
    final_script_name = f"script_{run_id}.json"
    final_caption_name = f"caption_{run_id}.txt"
    
    vault_video_path = os.path.join(vault_dir, final_video_name)
    vault_script_path = os.path.join(vault_dir, final_script_name)
    vault_caption_path = os.path.join(vault_dir, final_caption_name)
    
    # Save Video
    shutil.move(temp_video, vault_video_path)
    
    # Save Script Metadata JSON
    script_data["meta"] = {
        "run_id": run_id,
        "topic": topic,
        "theme": theme,
        "timestamp": timestamp
    }
    with open(vault_script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=4)
        
    # Save Ready-to-Copy Instagram Caption File
    caption_content = f"{script_data.get('title', topic).upper()}\n\n{script_data['voiceover_full']}\n\n#sovereign #execution #mindset #systems #identity"
    with open(vault_caption_path, "w", encoding="utf-8") as f:
        f.write(caption_content)
        
    print(f"=== Pipeline Complete! Asset Vaulted At: {vault_dir} ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MediaFactory Faceless Reel Generator")
    parser.add_argument("--topic", type=str, default="", help="Optional specific topic")
    parser.add_argument("--theme", type=str, default="", help="Optional specific theme")
    args = parser.parse_args()
    
    run_pipeline(args.topic, args.theme)
