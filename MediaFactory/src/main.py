import os
import argparse
from script_generator import generate_reel_content
from audio_generator import create_audio
from video_builder import build_video

def run_pipeline(topic: str, theme: str):
    print(f"=== Initiating MediaFactory Engine | Topic: '{topic}' | Theme: '{theme}' ===")
    
    # 1. Gemini Content & Visual Generation
    print("[1/3] Generating script & scene breakdown with Gemini...")
    script_data = generate_reel_content(topic)
    
    # 2. Audio Synthesis
    print("[2/3] Synthesizing voiceover track...")
    audio_file = "voice.mp3"
    create_audio(script_data["voiceover_full"], output_path=audio_file)
    
    # 3. Video Composition
    print(f"[3/3] Rendering video composition with [{theme.upper()}] design preset...")
    output_video = "final_reel.mp4"
    build_video(script_data, audio_path=audio_file, theme=theme, output_path=output_video)
    
    print("=== Pipeline Complete: Output saved as final_reel.mp4 ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MediaFactory Faceless Reel Generator")
    parser.add_argument("--topic", type=str, default="Sovereign Execution", help="Topic for the reel")
    parser.add_argument("--theme", type=str, choices=["sovereign", "ambient", "kinetic"], default="ambient", help="Design preset theme")
    args = parser.parse_args()
    
    run_pipeline(args.topic, args.theme)
