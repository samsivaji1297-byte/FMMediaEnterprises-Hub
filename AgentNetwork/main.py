import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Anchor repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from AgentNetwork.agents.grand_strategist import GrandStrategist
from AgentNetwork.agents.revenue_enforcer import RevenueEnforcer
from AgentNetwork.agents.vanguard_miner import VanguardMiner
from AgentNetwork.agents.writer import ScriptEngineAgent
from AgentNetwork.core.schemas import SignalPayload
from AgentNetwork.agents.publisher import InstagramPublisher
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

    # 3. Active Demand Intake (Directly targeting 'top_demand_angles' -> 'intent_phrase')
    demand_summary_path = REPO_ROOT / "vault" / "active_demand_summary.json"
    topic = None

    if demand_summary_path.exists():
        try:
            demand_data = json.loads(demand_summary_path.read_text(encoding="utf-8"))
            angles = demand_data.get("top_demand_angles", [])
            if isinstance(angles, list) and len(angles) > 0:
                topic = angles[0].get("intent_phrase") or angles[0].get("source_seed")
        except Exception as e:
            print(f"[!] DemandDatabase parse error: {e}")

    if not topic:
        miner = VanguardMiner()
        friction_payload = miner.mine_friction()
        topic = friction_payload.get("friction_point", "wasting time seeking comfort")

    print(f"[+] Selected Demand Execution Topic: '{topic}'")

    # 4. Writer Engine via ScriptEngineAgent (Native JSON Enforcement)
    print("\n=== [WRITER ENGINE]: Generating Dynamic Script & Blueprint ===")
    
    if enforce_status.get("status") == "EMERGENCY_PIVOT":
        print("[!] EMERGENCY PIVOT DETECTED: Forcing direct-response execution angle.")
        topic += " - FORCE IMMEDIATE DIRECT CONVERSION"

    signal = SignalPayload(
        universal_pain_point=topic,
        search_query=topic,
        target_hook=f"Stop losing hours to manual {topic}.",
        actionable_takeaway="Deploy automated infrastructure.",
        content_pillar="operator_sovereignty"
    )

    writer_agent = ScriptEngineAgent()
    script_payload = writer_agent.generate_script(signal)

    # Map ScriptPayload to dictionary blueprint structure required by video_builder
    blueprint = {
        "title": script_payload.title,
        "hook": script_payload.hook_text,
        "caption": f"{script_payload.hook_text}\n\n{script_payload.voiceover_script}\n\n{script_payload.call_to_action}\n\n#execution #automation #mindset #operator",
        "scenes": [
            {
                "scene_id": 1, 
                "text": script_payload.hook_text, 
                "visual_prompt": script_payload.visual_search_queries[0] if script_payload.visual_search_queries else "dark cyberpunk terminal"
            },
            {
                "scene_id": 2, 
                "text": script_payload.voiceover_script, 
                "visual_prompt": script_payload.visual_search_queries[1] if len(script_payload.visual_search_queries) > 1 else "glowing data feeds"
            },
            {
                "scene_id": 3, 
                "text": script_payload.call_to_action, 
                "visual_prompt": "obsidian dashboard gold highlights"
            }
        ]
    }

    # 5. MediaFactory Vault Renders & Debug Dump
    print("\n=== [MEDIAFACTORY]: Generating Audio & Video Assets ===")
    
    title_raw = blueprint.get("title", "relentless_execution")
    clean_title = "".join(c for c in title_raw if c.isalnum() or c in ("_", "-")).lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    title = f"{clean_title}_{timestamp}"

    vault_dir = REPO_ROOT / "vault" / "renders" / "archived"
    renders_dir = REPO_ROOT / "MediaFactory" / "vault" / "renders"
    audio_dir = REPO_ROOT / "MediaFactory" / "vault" / "audio"

    vault_dir.mkdir(parents=True, exist_ok=True)
    renders_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Write .txt Caption
    caption_text = blueprint.get("caption", f"{title.replace('_', ' ').title()}\n\n#execution #mindset #operator")
    (renders_dir / f"{title}.txt").write_text(caption_text, encoding="utf-8")

    # Write Full Script Debug Dump TXT file
    script_debug_path = renders_dir / f"{title}_full_script.txt"
    debug_dump = f"""=== GENERATED SCRIPT DEBUG DUMP ===
Timestamp: {timestamp}
Topic: {topic}
Title: {script_payload.title}
Hook: {script_payload.hook_text}
Voiceover Script: {script_payload.voiceover_script}
Call to Action: {script_payload.call_to_action}
Theme: {script_payload.theme}

--- SCENES ---
"""
    for scene in blueprint.get("scenes", []):
        debug_dump += f"Scene {scene.get('scene_id')}:\n  Text: {scene.get('text')}\n  Visual Prompt: {scene.get('visual_prompt')}\n\n"

    script_debug_path.write_text(debug_dump, encoding="utf-8")
    print(f"[✓] Full script debug dump saved to: {script_debug_path.name}")

    # Audio & Video Generation
    full_voiceover_text = script_payload.voiceover_script
    audio_path = audio_dir / f"{title}_audio.mp3"
    
    generate_voiceover_failsafe(text=full_voiceover_text, output_path=str(audio_path))

    try:
        from MediaFactory.src.video_builder import build_video
        output_video_path = renders_dir / f"{title}.mp4"
        build_video(
            blueprint, 
            str(audio_path),
            str(output_video_path)
        )
        print(f"\n[SUCCESS] Render Complete: {output_video_path}")
    except Exception as e:
        print(f"[!] Video Rendering failed: {e}")

    # 6. Instagram Publisher: Dispatch Pending Reels to Instagram via Meta Graph API
    print("\n=== [INSTAGRAM PUBLISHER]: DISPATCHING PENDING REELS ===")
    publisher = InstagramPublisher()
    publisher.publish_pending_reels()

    # AUTO-ARCHIVE (Hardened against dictionary structures)
    archive_dir = renders_dir / "archived"
    archive_dir.mkdir(parents=True, exist_ok=True)
    published_tracker = REPO_ROOT / "vault" / "published_reels.json"

    if published_tracker.exists():
        try:
            published_data = json.loads(published_tracker.read_text(encoding="utf-8"))
            if isinstance(published_data, dict):
                published_files = set(published_data.keys())
            elif isinstance(published_data, list):
                published_files = set(str(item) for item in published_data)
            else:
                published_files = set()
            
            for render_file in renders_dir.glob("*.mp4"):
                if render_file.name in published_files or any(f in render_file.name for f in published_files):
                    render_file.rename(archive_dir / render_file.name)
                    caption_file = render_file.with_suffix(".txt")
                    if caption_file.exists():
                        caption_file.rename(archive_dir / caption_file.name)
                    debug_txt_file = render_file.with_name(render_file.stem + "_full_script.txt")
                    if debug_txt_file.exists():
                        debug_txt_file.rename(archive_dir / debug_txt_file.name)
                    print(f"[✓] Archived published asset & debug dump: {render_file.name}")
        except Exception as e:
            print(f"[!] Archival Check Warning: {e}")

    # 7. Instagram Analytics Agent: Scrape Performance & Train Intelligence Memory
    analytics_agent = InstagramAnalyticsAgent()
    analytics_agent.update_intelligence()

    # 8. SalesDMOperator: Scans inbound post comments, dispatches conversion DMs, and feeds sales logs back to RevenueEnforcer
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
