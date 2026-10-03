import sys
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from GrowthAgent.core.reels_engine import generate_psychology_reel
from GrowthAgent.analytics.meta_tracker import fetch_reel_metrics, record_reel_performance
from GrowthAgent.core.feedback_loop import run_self_optimization_cycle


def run_agent_pipeline(product_key: str = None, simulate_publish: bool = True):
    print("=" * 70)
    print("      AUTONOMOUS GROWTH AGENT :: REELS PSYCHOLOGY PIPELINE     ")
    print("=" * 70)

    # 1. Generate High-Retention Script
    print("\n[PHASE 1] Synthesizing High-Retention Reel Script...")
    script_data = generate_psychology_reel(product_key)
    print(f"[+] Script Title: {script_data.get('title')}")
    print(f"[+] Target Product: {script_data.get('product_key')}")

    # Output JSON bundle for MediaFactory / Rendering engine consumption
    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"growth_reel_{script_data.get('product_key')}.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2)
    print(f"[+] Asset payload saved to: {out_file.relative_to(PROJECT_ROOT)}")

    # 2. Analytics Tracking Simulation / Real Meta Sync
    if simulate_publish:
        print("\n[PHASE 2] Syncing Meta API Analytics...")
        simulated_media_id = f"ig_reel_{script_data.get('product_key')}_001"
        metrics = fetch_reel_metrics(simulated_media_id)
        record_reel_performance(simulated_media_id, script_data, metrics)

    # 3. Autonomous Optimization Loop
    print("\n[PHASE 3] Running Autonomous Self-Optimization Loop...")
    run_self_optimization_cycle()

    print("\n[SUCCESS] Growth Agent execution loop completed cleanly.")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    run_agent_pipeline(product_key=target)
