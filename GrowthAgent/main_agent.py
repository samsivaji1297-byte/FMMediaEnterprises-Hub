import os
import sys
import json
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Dynamically import reels_engine to support function or class methods
import GrowthAgent.core.reels_engine as reels_engine
from GrowthAgent.analytics.meta_tracker import publish_reel_to_instagram, record_reel_performance, fetch_reel_metrics
from GrowthAgent.core.feedback_loop import run_optimization_cycle


def synthesize_script(product_key: str) -> dict:
    """Helper to call whichever generator function exists in reels_engine."""
    if hasattr(reels_engine, "generate_reel_script"):
        return reels_engine.generate_reel_script(product_key)
    elif hasattr(reels_engine, "generate_script"):
        return reels_engine.generate_script(product_key)
    elif hasattr(reels_engine, "ReelsEngine"):
        engine = reels_engine.ReelsEngine()
        if hasattr(engine, "generate"):
            return engine.generate(product_key)
        elif hasattr(engine, "generate_script"):
            return engine.generate_script(product_key)
    
    raise AttributeError("No valid script generation function found in reels_engine.py")


def run_pipeline(product_key: str = "TIMELINE_REJECTION"):
    print("=" * 70)
    print("      AUTONOMOUS GROWTH AGENT :: REELS PSYCHOLOGY PIPELINE     ")
    print("=" * 70)

    # ------------------------------------------------------------------
    # PHASE 1: Synthesize High-Retention Script Payload
    # ------------------------------------------------------------------
    print("\n[PHASE 1] Synthesizing High-Retention Reel Script...")
    script_payload = synthesize_script(product_key=product_key)
    
    title = script_payload.get("title", "Growth Reel")
    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    payload_file = output_dir / f"growth_reel_{product_key}.json"
    
    with open(payload_file, "w", encoding="utf-8") as f:
        json.dump(script_payload, f, indent=2)

    print(f"[+] Script Title: {title}")
    print(f"[+] Target Product: {product_key}")
    print(f"[+] Asset payload saved to: {payload_file}")

    # ------------------------------------------------------------------
    # PHASE 2: Live IG Publish or Video Processing Check
    # ------------------------------------------------------------------
    print("\n[PHASE 2] Executing Meta API Upload & Analytics Sync...")

    video_url = script_payload.get("video_url") or os.environ.get("REEL_VIDEO_URL")
    
    scenes_text = "\n".join([f"• {s.get('text_overlay', '')}" for s in script_payload.get("scenes", [])])
    caption = f"{title}\n\n{scenes_text}\n\n#sovereignty #productivity #mindset #automation"

    media_id = None
    if video_url:
        print(f"[*] Live video target detected: {video_url}")
        media_id = publish_reel_to_instagram(video_url=video_url, caption=caption)
    else:
        print("[!] Note: No public MP4 video_url supplied in payload or REEL_VIDEO_URL env var.")
        print("[*] Script payload generated successfully. To auto-upload video files directly, pass REEL_VIDEO_URL or link to Drive/GitHub MP4 host.")

    if not media_id:
        media_id = f"ig_reel_{product_key}_{os.urandom(3).hex()}"
        print(f"[*] Registered run tracking ID: {media_id}")

    metrics = fetch_reel_metrics(media_id)
    record_reel_performance(media_id, script_payload, metrics)

    # ------------------------------------------------------------------
    # PHASE 3: Autonomous Prompt Optimization Loop
    # ------------------------------------------------------------------
    print("\n[PHASE 3] Running Autonomous Self-Optimization Loop...")
    run_optimization_cycle()

    print("\n[SUCCESS] Growth Agent execution loop completed cleanly.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GrowthAgent Pipeline Execution")
    parser.add_argument("product_key", nargs="?", default="TIMELINE_REJECTION", help="Target product key")
    args = parser.parse_args()

    run_pipeline(product_key=args.product_key)
