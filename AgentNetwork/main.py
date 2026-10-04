import argparse
from AgentNetwork.core.schemas import ExecutionConfig
from AgentNetwork.agents.miner import SignalMinerAgent
from AgentNetwork.agents.writer import ScriptEngineAgent
from AgentNetwork.core.bridge import MediaFactoryBridge

def run_pipeline(mode: str = "single", count: int = 1):
    print(f"=== KICKING OFF AGENT NETWORK [{mode.upper()} MODE] ===")
    
    config = ExecutionConfig(mode=mode, batch_size=count)
    miner = SignalMinerAgent()
    writer = ScriptEngineAgent()
    bridge = MediaFactoryBridge()

    # Step 1: Extract Demand Signals
    print("\n[1/3] Mining Demand & Friction Signals...")
    signals = miner.extract_signals(config)

    for i, sig in enumerate(signals, 1):
        print(f"\n--- Processing Signal {i}/{len(signals)} [{sig.signal_id}] ---")
        print(f"Demand Source: {sig.demand_type} | Friction: {sig.universal_pain_point}")

        # Step 2: Write Script
        print("[2/3] Generating High-Retention Script...")
        script = writer.generate_script(sig)
        print(f"Script Title: {script.title}")
        print(f"Hook: '{script.hook_text}'")

        # Step 3: Render via MediaFactory
        print("[3/3] Compositing Asset via MediaFactory...")
        video_path = bridge.render_script(script)
        print(f"[✓] Asset ready for distribution: {video_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent Network Orchestrator")
    parser.add_argument("--mode", choices=["single", "batch"], default="single", help="Execution mode")
    parser.add_argument("--count", type=int, default=1, help="Batch count")
    args = parser.parse_args()

    run_pipeline(mode=args.mode, count=args.count)
