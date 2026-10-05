import argparse
from pathlib import Path
from AgentNetwork.agents.miner import FrictionMiner
from AgentNetwork.agents.writer import ScriptWriter
from AgentNetwork.core.bridge import MediaFactoryBridge
from AgentNetwork.agents.publisher import InstagramPublisher

def run_pipeline(mode: str = "single", count: int = 1):
    print("=== KICKING OFF AGENT NETWORK [SINGLE MODE] ===")

    # Step 1: Mine Signals
    print("\n[1/4] Mining Demand & Friction Signals...")
    miner = FrictionMiner()
    signals = miner.mine_signals(count=count)

    writer = ScriptWriter()
    bridge = MediaFactoryBridge()
    publisher = InstagramPublisher()

    for idx, signal in enumerate(signals, 1):
        print(f"\n--- Processing Signal {idx}/{len(signals)} [{signal.id}] ---")
        print(f"Demand Source: {signal.source} | Friction: {signal.friction_text}")

        # Step 2: Generate Script Payload
        print("[2/4] Generating High-Retention Script...")
        script = writer.generate_script(signal)
        print(f"Script Title: {script.title}")
        print(f"Hook: '{script.hook_text}'")

        # Step 3: Composite Video Asset
        print("[3/4] Compositing Asset via MediaFactory...")
        video_path = bridge.render_script(script)
        print(f"[✓] Render Complete: {video_path}")

        # Step 4: Publish to Instagram Reels via Meta Graph API
        print("[4/4] Dispatching to Instagram Reels...")
        caption = f"{script.title}\n\n{script.hook_text}\n\n{script.call_to_action}\n\n#systems #automation #mindset #productivity"
        publisher.publish_reel(Path(video_path), caption)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent Network Autopilot")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "batch"])
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    run_pipeline(mode=args.mode, count=args.count)
