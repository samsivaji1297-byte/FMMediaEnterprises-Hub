import argparse
import inspect
from pathlib import Path

import AgentNetwork.agents.miner as miner_module
import AgentNetwork.agents.writer as writer_module
from AgentNetwork.core.bridge import MediaFactoryBridge
from AgentNetwork.agents.publisher import InstagramPublisher


def _get_module_class(module, module_name: str):
    """Finds and returns the primary class defined inside a module."""
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__:
            return obj
    raise ImportError(f"No class definition found in {module_name}")


# Dynamically bind miner and writer classes regardless of internal naming
miner_class = _get_module_class(miner_module, "AgentNetwork/agents/miner.py")
writer_class = _get_module_class(writer_module, "AgentNetwork/agents/writer.py")


def run_pipeline(mode: str = "single", count: int = 1):
    print("=== KICKING OFF AGENT NETWORK [SINGLE MODE] ===")

    # Step 1: Mine Signals
    print("\n[1/4] Mining Demand & Friction Signals...")
    miner = miner_class()
    mine_func = (
        getattr(miner, "mine_signals", None)
        or getattr(miner, "run", None)
        or getattr(miner, "mine", None)
    )
    signals = mine_func(count=count) if mine_func else []

    writer = writer_class()
    bridge = MediaFactoryBridge()
    publisher = InstagramPublisher()

    for idx, signal in enumerate(signals, 1):
        sig_id = getattr(signal, "id", f"sig_{idx}")
        sig_src = getattr(signal, "source", "evergreen_utility")
        sig_text = getattr(signal, "friction_text", getattr(signal, "text", ""))

        print(f"\n--- Processing Signal {idx}/{len(signals)} [{sig_id}] ---")
        print(f"Demand Source: {sig_src} | Friction: {sig_text}")

        # Step 2: Generate Script Payload
        print("[2/4] Generating High-Retention Script...")
        generate_func = (
            getattr(writer, "generate_script", None)
            or getattr(writer, "write", None)
            or getattr(writer, "run", None)
        )
        script = generate_func(signal)

        print(f"Script Title: {getattr(script, 'title', 'Untitled')}")
        print(f"Hook: '{getattr(script, 'hook_text', getattr(script, 'hook', ''))}'")

        # Step 3: Composite Video Asset
        print("[3/4] Compositing Asset via MediaFactory...")
        video_path = bridge.render_script(script)
        print(f"[✓] Render Complete: {video_path}")

        # Step 4: Publish to Instagram Reels via Meta Graph API
        print("[4/4] Dispatching to Instagram Reels...")
        caption = (
            f"{getattr(script, 'title', '')}\n\n"
            f"{getattr(script, 'hook_text', getattr(script, 'hook', ''))}\n\n"
            f"{getattr(script, 'call_to_action', getattr(script, 'cta', ''))}\n\n"
            f"#systems #automation #mindset #productivity"
        )
        publisher.publish_reel(Path(video_path), caption)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent Network Autopilot")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "batch"])
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    run_pipeline(mode=args.mode, count=args.count)
