import argparse
import inspect
from pathlib import Path
from dataclasses import dataclass, field

import AgentNetwork.agents.miner as miner_module
import AgentNetwork.agents.writer as writer_module
from AgentNetwork.core.bridge import MediaFactoryBridge
from AgentNetwork.agents.publisher import InstagramPublisher


@dataclass
class FallbackSignal:
    id: str = "sig_fallback_01"
    source: str = "evergreen_utility"
    friction_text: str = "The exhausting cognitive overload of managing manual repetitive tasks every single day."
    universal_pain_point: str = "Spending hours on repetitive manual workflows instead of high-value strategic work."
    market_demand_score: float = 0.95
    category: str = "productivity"
    target_audience: str = "creators and operators"


class SafeSignalProxy:
    """Wraps any signal object to automatically provide safe defaults for missing attributes."""
    def __init__(self, target):
        self._target = target

    def __getattr__(self, name):
        if hasattr(self._target, name):
            return getattr(self._target, name)
        # Safe default attribute fallbacks for prompt templates
        defaults = {
            "universal_pain_point": getattr(self._target, "friction_text", "manual task fatigue"),
            "friction_text": "repetitive manual process bottlenecks",
            "market_demand_score": 0.90,
            "category": "automation",
            "target_audience": "operators",
            "source": "evergreen_utility",
            "id": "sig_auto_01",
        }
        return defaults.get(name, "high execution leverage")


def _get_module_class(module, module_name: str):
    """Finds and returns the primary class defined inside a module."""
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__:
            return obj
    raise ImportError(f"No class definition found in {module_name}")


# Dynamically bind miner and writer classes
miner_class = _get_module_class(miner_module, "AgentNetwork/agents/miner.py")
writer_class = _get_module_class(writer_module, "AgentNetwork/agents/writer.py")


def run_pipeline(mode: str = "single", count: int = 1):
    print("=== KICKING OFF AGENT NETWORK [SINGLE MODE] ===")

    # Step 1: Mine Signals
    print("\n[1/4] Mining Demand & Friction Signals...")
    try:
        miner = miner_class()
        mine_func = (
            getattr(miner, "mine_signals", None)
            or getattr(miner, "run", None)
            or getattr(miner, "mine", None)
        )
        signals = mine_func(count=count) if mine_func else []
    except Exception as e:
        print(f"[!] Miner execution warning: {e}")
        signals = []

    # FALLBACK GUARANTEE: Never exit empty
    if not signals:
        print("[*] Miner returned 0 signals. Injecting fallback friction signal to force execution pipeline...")
        signals = [FallbackSignal()]

    writer = writer_class()
    bridge = MediaFactoryBridge()
    publisher = InstagramPublisher()

    for idx, raw_signal in enumerate(signals, 1):
        # Wrap signal in proxy to protect writer against missing fields
        signal = SafeSignalProxy(raw_signal)

        print(f"\n--- Processing Signal {idx}/{len(signals)} [{signal.id}] ---")
        print(f"Demand Source: {signal.source} | Friction: {signal.friction_text}")

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
