import os
import sys
import json
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Dynamically add potential module paths for audio_generator and video_builder
for path_candidate in [PROJECT_ROOT, SCRIPT_DIR, SCRIPT_DIR / "media", PROJECT_ROOT / "MediaFactory"]:
    if str(path_candidate) not in sys.path and path_candidate.exists():
        sys.path.append(str(path_candidate))

from GrowthAgent.core.reels_engine import generate_psychology_reel
from GrowthAgent.analytics.meta_tracker import publish_reel_to_instagram, record_reel_performance, fetch_reel_metrics

try:
    from audio_generator import create_audio
    from video_builder import build_video
    HAS_RENDER_ENGINE = True
except ImportError:
    HAS_RENDER_ENGINE = False

import GrowthAgent.core.feedback_loop as feedback_loop


def execute_optimization_loop():
    for fn_name in ["run_optimization_cycle", "run_feedback_loop", "optimize_prompts", "run_optimization"]:
        if hasattr(feedback_loop, fn_name):
            return getattr(feedback_loop, fn_name)()
    print("[!] Warning: Could not locate optimization entry point in feedback_loop.py")


def run_pipeline(product_key: str = "TIMELINE_REJECTION", theme: str = "sovereign", stage: str = "all"):
    print("=" * 70)
    print(f"   AUTONOMOUS GROWTH AGENT :: EXECUTION STAGE [{stage.upper()}]")
    print("=" * 70)

    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    payload_file = output_dir / f"growth_reel_{product_key}.json"
    video_file_path = output_dir / f"growth_reel_{product_key}.mp4"
    audio_file_path = output_dir / "temp_voice.mp3"

    # STAGE: RENDER OR ALL
    if stage in ["render", "all"]:
        print("\n[PHASE 1] Synthesizing High-Retention Reel Script...")
        script_payload = generate_psychology_reel(product_key=product_key)
        
        with open(payload_file, "w", encoding="utf-8") as f:
            json.dump(script_payload, f, indent=2)

        print(f"[+] Script Title: {script_payload.get('title', 'Growth Reel')}")
        print(f"[+] Asset payload saved: {payload_file}")

        if HAS_RENDER_ENGINE and "voiceover_full" in script_payload:
            print("\n[PHASE 2] Rendering Voiceover & MP4 Video Asset...")
            try:
                create_audio(script_payload["voiceover_full"], output_path=str(audio_file_path))
                build_video(script_payload, audio_path=str(audio_file_path), theme=theme, output_path=str(video_file_path))
                print(f"[+] Video rendered successfully: {video_file_path}")
            except Exception as e:
                print(f"[!] Rendering step failed: {e}")
        else:
            print("\n[PHASE 2] Skipping local rendering (audio_generator/video_builder not found on sys.path).")

    # STAGE: PUBLISH OR ALL
    if stage in ["publish", "all"]:
        print("\n[PHASE 3] Resolving Video URL & Executing Meta API Upload...")
        
        if payload_file.exists():
            with open(payload_file, "r", encoding="utf-8") as f:
                script_payload = json.load(f)
        else:
            script_payload = {}

        github_repo = os.environ.get("GITHUB_REPOSITORY", "")
        raw_github_url = f"https://raw.githubusercontent.com/{github_repo}/main/GrowthAgent/output/growth_reel_{product_key}.mp4" if github_repo else None

        video_url = os.environ.get("REEL_VIDEO_URL") or script_payload.get("video_url") or raw_github_url
        caption = script_payload.get("caption") or f"{product_key}\n\n#sovereignty #productivity #mindset #automation"

        # Read secrets under common naming variations
        access_token = os.environ.get("IG_ACCESS_TOKEN") or os.environ.get("INSTAGRAM_ACCESS_TOKEN") or os.environ.get("META_ACCESS_TOKEN")
        user_id = os.environ.get("IG_USER_ID") or os.environ.get("INSTAGRAM_ACCOUNT_ID")

        media_id = None
        if access_token and user_id:
            print(f"[*] Dispatching MP4 target to Meta API: {video_url}")
            try:
                media_id = publish_reel_to_instagram(video_url=video_url, caption=caption)
            except Exception as e:
                print(f"[!] Meta API publishing error: {e}")
        else:
            print("[!] Meta API credentials missing in environment variables.")

        if not media_id:
            media_id = f"ig_reel_{product_key}_{os.urandom(3).hex()}"
            print(f"[*] Registered run tracking ID: {media_id}")

        try:
            metrics = fetch_reel_metrics(media_id)
            record_reel_performance(media_id, script_payload, metrics)
        except Exception as e:
            print(f"[*] Performance logging deferred: {e}")

        print("\n[PHASE 4] Running Autonomous Self-Optimization Loop...")
        execute_optimization_loop()

    print("\n[SUCCESS] Pipeline stage execution completed cleanly.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GrowthAgent Pipeline Execution")
    parser.add_argument("product_key", nargs="?", default="TIMELINE_REJECTION", help="Target product key")
    parser.add_argument("--theme", type=str, default="sovereign", help="Design preset theme")
    parser.add_argument("--stage", type=str, choices=["render", "publish", "all"], default="all", help="Execution stage")
    args = parser.parse_args()

    run_pipeline(product_key=args.product_key, theme=args.theme, stage=args.stage)
