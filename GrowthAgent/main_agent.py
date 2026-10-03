import os
import sys
import json
import argparse
import inspect
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Import modules directly to inspect available functions
import GrowthAgent.core.reels_engine as reels_engine
import GrowthAgent.core.feedback_loop as feedback_loop
from GrowthAgent.analytics.meta_tracker import publish_reel_to_instagram, record_reel_performance, fetch_reel_metrics


def synthesize_script(product_key: str) -> dict:
    """Helper to dynamically trigger the generation function in reels_engine."""
    for fn_name in ["generate_reel_script", "generate_script", "run_script_generation", "generate"]:
        if hasattr(reels_engine, fn_name):
            return getattr(reels_engine, fn_name)(product_key)
            
    if hasattr(reels_engine, "ReelsEngine"):
        engine = reels_engine.ReelsEngine()
        for method_name in ["generate", "generate_script", "run"]:
            if hasattr(engine, method_name):
                return getattr(engine, method_name)(product_key)
                
    raise AttributeError("Could not find a valid generation function in reels_engine.py")


def execute_optimization_loop():
    """Helper to dynamically trigger the optimization function in feedback_loop."""
    for fn_name in ["run_optimization_cycle", "run_feedback_loop", "optimize_prompts", "run_optimization", "main"]:
        if hasattr(feedback_loop, fn_name):
            func = getattr(feedback_loop, fn_name)
            # Check if function takes arguments or run empty
            sig = inspect.signature(func)
            if len(sig.parameters) == 0:
                return func()
            else:
                return func()
                
    if hasattr(feedback_loop, "FeedbackLoop"):
        loop = feedback_loop.FeedbackLoop()
        for method_name in ["run", "optimize", "execute"]:
            if hasattr(loop, method_name):
                return getattr(loop, method_name)()

    print("[!] Warning: Could not find optimization function in feedback_loop.py. Skipping phase.")


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
    
    scenes = script_payload.get("scenes", [])
    scenes_text = "\n".join([f"• {s.get('text_overlay', '')}" for s in scenes]) if isinstance(scenes, list) else ""
    caption = f"{title}\n\n{scenes_text}\n\n#sovereignty #productivity #mindset #automation"

    media_id = None
    if video_url:
        print(f"[*] Live video target detected: {video_url}")
        media_id = publish_reel_to_instagram(video_url=video_url, caption=caption)
    else:
        print("[!] Note: No public MP4 video_url supplied in payload or REEL_VIDEO_URL env var.")

    if not media_id:
        media_id = f"ig_reel_{product_key}_{os.urandom(3).hex()}"
        print(f"[*] Registered run tracking ID: {media_id}")

    try:
        metrics = fetch_reel_metrics(media_id)
        record_reel_performance(media_id, script_payload, metrics)
    except Exception as e:
        print(f"[*] Performance logging skipped/deferred: {e}")

    # ------------------------------------------------------------------
    # PHASE 3: Autonomous Prompt Optimization Loop
    # ------------------------------------------------------------------
    print("\n[PHASE 3] Running Autonomous Self-Optimization Loop...")
    execute_optimization_loop()

    print("\n[SUCCESS] Growth Agent execution loop completed cleanly.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GrowthAgent Pipeline Execution")
    parser.add_argument("product_key", nargs="?", default="TIMELINE_REJECTION", help="Target product key")
    args = parser.parse_args()

    run_pipeline(product_key=args.product_key)
