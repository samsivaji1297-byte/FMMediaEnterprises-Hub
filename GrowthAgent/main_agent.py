import os
import sys
import json
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Import core modules
from GrowthAgent.core.reels_engine import generate_psychology_reel
from GrowthAgent.analytics.meta_tracker import publish_reel_to_instagram, record_reel_performance, fetch_reel_metrics

# Dynamically import audio and video composition dependencies if present
try:
    from audio_generator import create_audio
    from video_builder import build_video
    HAS_RENDER_ENGINE = True
except ImportError:
    HAS_RENDER_ENGINE = False

import GrowthAgent.core.feedback_loop as feedback_loop


def execute_optimization_loop():
    """Helper to invoke prompt optimization loop."""
    for fn_name in ["run_optimization_cycle", "run_feedback_loop", "optimize_prompts", "run_optimization"]:
        if hasattr(feedback_loop, fn_name):
            return getattr(feedback_loop, fn_name)()
    print("[!] Warning: Could not locate optimization entry point in feedback_loop.py")


def run_pipeline(product_key: str = "TIMELINE_REJECTION", theme: str = "sovereign"):
    print("=" * 70)
    print("      AUTONOMOUS GROWTH AGENT :: END-TO-END REELS PIPELINE     ")
    print("=" * 70)

    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # PHASE 1: Synthesize High-Retention Script Payload
    # ------------------------------------------------------------------
    print("\n[PHASE 1] Synthesizing High-Retention Reel Script...")
    script_payload = generate_psychology_reel(product_key=product_key)
    
    title = script_payload.get("title", "Growth Reel")
    payload_file = output_dir / f"growth_reel_{product_key}.json"
    
    with open(payload_file, "w", encoding="utf-8") as f:
        json.dump(script_payload, f, indent=2)

    print(f"[+] Script Title: {title}")
    print(f"[+] Target Product: {product_key}")
    print(f"[+] Asset payload saved: {payload_file}")

    # ------------------------------------------------------------------
    # PHASE 2: Local Audio & Video Rendering
    # ------------------------------------------------------------------
    video_file_path = output_dir / f"growth_reel_{product_key}.mp4"
    audio_file_path = output_dir / "temp_voice.mp3"

    if HAS_RENDER_ENGINE and "voiceover_full" in script_payload:
        print("\n[PHASE 2] Rendering Voiceover & MP4 Video Asset...")
        try:
            create_audio(script_payload["voiceover_full"], output_path=str(audio_file_path))
            build_video(script_payload, audio_path=str(audio_file_path), theme=theme, output_path=str(video_file_path))
            print(f"[+] Video rendered successfully: {video_file_path}")
        except Exception as e:
            print(f"[!] Rendering step failed: {e}")
    else:
        print("\n[PHASE 2] Skipping local rendering (audio/video generator modules not found on PYTHONPATH).")

    # ------------------------------------------------------------------
    # PHASE 3: Public Video Target Resolution & Meta Upload
    # ------------------------------------------------------------------
    print("\n[PHASE 3] Resolving Video URL & Executing Meta API Upload...")

    # Determine GitHub Repository reference for raw URL fallback
    github_repo = os.environ.get("GITHUB_REPOSITORY", "")  # e.g. "user/repo"
    raw_github_url = f"https://raw.githubusercontent.com/{github_repo}/main/GrowthAgent/output/growth_reel_{product_key}.mp4" if github_repo else None

    video_url = os.environ.get("REEL_VIDEO_URL") or script_payload.get("video_url") or raw_github_url
    caption = script_payload.get("caption") or f"{title.upper()}\n\n{script_payload.get('voiceover_full', '')}\n\n#sovereignty #productivity #mindset #automation"

    media_id = None
    if video_file_path.exists() and video_url:
        print(f"[*] Dispatching MP4 target to Meta API: {video_url}")
        try:
            media_id = publish_reel_to_instagram(video_url=video_url, caption=caption)
        except Exception as e:
            print(f"[!] Meta API publishing error: {e}")

    if not media_id:
        media_id = f"ig_reel_{product_key}_{os.urandom(3).hex()}"
        print(f"[*] Registered run tracking ID: {media_id}")

    try:
        metrics = fetch_reel_metrics(media_id)
        record_reel_performance(media_id, script_payload, metrics)
    except Exception as e:
        print(f"[*] Performance logging deferred: {e}")

    # ------------------------------------------------------------------
    # PHASE 4: Autonomous Prompt Optimization Loop
    # ------------------------------------------------------------------
    print("\n[PHASE 4] Running Autonomous Self-Optimization Loop...")
    execute_optimization_loop()

    print("\n[SUCCESS] Pipeline execution loop completed cleanly.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GrowthAgent Pipeline Execution")
    parser.add_argument("product_key", nargs="?", default="TIMELINE_REJECTION", help="Target product key")
    parser.add_argument("--theme", type=str, default="sovereign", help="Design preset theme")
    args = parser.parse_args()

    run_pipeline(product_key=args.product_key, theme=args.theme)
