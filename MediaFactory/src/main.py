import os
import argparse
from script_generator import generate_reel_content
from audio_generator import create_audio
from video_builder import build_video

def run_pipeline(topic: str):
    print(f"=== Initiating MediaFactory Reel Engine | Topic: '{topic}' ===")

    # 1. Gemini Content Generation
    print("[1/3] Generating script & scene breakdown with Gemini...")
    script_data = generate_reel_content(topic)

    # 2. Audio Synthesis
    print("[2/3] Synthesizing voiceover track...")
    audio_file = "voice.mp3"
    create_audio(script_data["voiceover_full"], output_path=audio_file)

    # 3. Video Rendering
    print("[3/3] Rendering video composition...")
    output_video = "final_reel.mp4"
    build_video(script_data, audio_path=audio_file, output_path=output_video)

    print("=== Pipeline Complete: Output saved as final_reel.mp4 ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MediaFactory Faceless Reel Generator")
    parser.add_argument("--topic", type=str, default="Sovereign Execution", help="Topic for the reel")
    args = parser.parse_args()

    run_pipeline(args.topic)
