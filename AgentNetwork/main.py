import sys
import os
import json
import argparse
from pathlib import Path

# Anchor repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from AgentNetwork.agents.grand_strategist import GrandStrategist
from AgentNetwork.agents.revenue_enforcer import RevenueEnforcer
from AgentNetwork.agents.vanguard_miner import VanguardMiner
from AgentNetwork.agents.mindset_agents import SovereignStrategist, KineticScriptwright
from AgentNetwork.agents.analytics_agent import InstagramAnalyticsAgent
from AgentNetwork.agents.sales_agent import SalesDMOperator

def generate_voiceover_failsafe(text: str, output_path: str):
    """Generates TTS audio with zero dependency on local sub-modules."""
    try:
        from MediaFactory.src import tts
        if hasattr(tts, "generate_voiceover"):
            tts.generate_voiceover(text=text, output_path=output_path)
            return
        elif hasattr(tts, "generate_tts"):
            tts.generate_tts(text=text, output_path=output_path)
            return
    except Exception:
        pass

    try:
        from gtts import gTTS
        tts_obj = gTTS(text=text, lang="en", slow=False)
        tts_obj.save(output_path)
        print(f"[✓] Voiceover generated via gTTS engine")
    except Exception as e:
        print(f"[!] Failsafe TTS Generation Error: {e}")
        raise e

def run_war_room_pipeline():
    print("\n=======================================================")
    print("      DIGITAL WAR ROOM // FULL FLEET EXECUTION         ")
    print("=======================================================\n")

    # 1. Grand Strategist: Evaluate War Map Fronts
    strategist = GrandStrategist()
    war_state = strategist.evaluate_strategy()

    # 2. Revenue Enforcer: Check Daily Baseline
    enforcer = RevenueEnforcer(target_daily_conversions=1)
    enforce_status = enforcer.enforce()

    # 3. Vanguard Miner: Extract Friction Seed
    miner = VanguardMiner()
    friction_payload = miner.mine_friction()

    # 4. Sovereign Strategist & Kinetic Scriptwright Generation
    print("\n=== [MINDSET ENGINE]: Drafting Hooks & Kinetic Scene Map ===")
    
    topic = friction_payload.get("friction_point", "wasting time seeking comfort")
    if enforce_status.get("status") == "EMERGENCY_PIVOT":
        print("[!] EMERGENCY PIVOT DETECTED: Forcing direct-response CTA template.")
        topic += " - FORCE IMMEDIATE DIRECT CONVERSION"

    sovereign = SovereignStrategist()
    strategy = sovereign.generate_strategy(topic)

    scriptwright = KineticScriptwright()
    blueprint = scriptwright.compile_blueprint(strategy)

    # 5. MediaFactory Vault Renders
    print("\n=== [MEDIAFACTORY]: Generating Audio & Video Assets ===")
    title_raw = blueprint.get("title", "relentless_execution")
    title = "".join(c for c in title_raw if c.isalnum() or c in ("_", "-")).lower()

    vault_dir = REPO_ROOT / "vault"
    renders_dir = REPO_ROOT / "MediaFactory" / "vault" / "renders"
    audio_dir = REPO_ROOT / "MediaFactory" / "vault" / "audio"

    vault_dir.mkdir(parents=True, exist_ok=True)
    renders_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Write .txt Caption
    caption_text = blueprint.get("caption", f"{title.replace('_', ' ').title()}\n\n#execution #mindset #operator")
    (renders_dir / f"{title}.txt").write_text(caption_text, encoding="utf-8")

    # Audio & Video Generation
    full_voiceover_text = " ".join([s.get("text", "") for s in blueprint.get("scenes", [])])
    audio_path = audio_dir / f"{title}_audio.mp3"
    
    generate_voiceover_failsafe(text=full_voiceover_text, output_path=str(audio_path))

    try:
        from MediaFactory.src.video_builder import build_video
        output_video_path = build_video(
            script_data=blueprint, 
            audio_path=str(audio_path),
            output_filename=f"{title}.mp4"
        )
        print(f"\n[SUCCESS] Render Complete: {output_video_path}")
    except Exception as e:
        print(f"[!] Video Rendering failed: {e}")

    # 6. Instagram Analytics Agent: Scrape Performance & Train Intelligence Memory
    analytics_agent = InstagramAnalyticsAgent()
    analytics_agent.update_intelligence()

    # 7. SalesDMOperator: Scans inbound post comments, dispatches conversion DMs, and feeds sales logs back to RevenueEnforcer
    print("\n[+] Triggering Direct-Response Sales & DM Operator...")
    sales_op = SalesDMOperator()
    sales_op.run_sales_sweep()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Digital War Room Fleet Pipeline.")
    parser.add_argument("--mode", type=str, default="single")
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    for i in range(args.count):
        run_war_room_pipeline()
