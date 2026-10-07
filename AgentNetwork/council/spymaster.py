import json
from pathlib import Path
from datetime import datetime
from AgentNetwork.council.state_manager import StateManager

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PUBLISHED_REELS_PATH = REPO_ROOT / "vault" / "published_reels.json"

class HighReconSpymaster:
    def __init__(self):
        self.state_mgr = StateManager()

    def gather_recon_intelligence((self) -> dict:
        print("\n=== [HIGH RECON SPYMASTER]: EXECUTING INTEL & AUDIENCE RECONNAISSANCE ===")
        
        reels_data = []
        if PUBLISHED_REELS_PATH.exists():
            try:
                with open(PUBLISHED_REELS_PATH, "r", encoding="utf-8") as f:
                    reels_data = json.load(f)
            except Exception as e:
                print(f"[!] Intel gathering warning (reels log read failed): {e}")

        # High-converting triggers based on audience response patterns
        winning_angles = [
            "Manual labor vs Autonomous pipeline architecture",
            "Zero-tolerance execution for high-frequency time-sinks",
            "Monetizing automated background execution circuits"
        ]

        total_published = len([x for x in reels_data if isinstance(x, dict)])
        
        intel_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_published_reels": total_published,
            "recommended_primary_angle": winning_angles[0] if total_published % 2 == 0 else winning_angles[1],
            "high_yield_keywords": ["PIPELINE", "AUTOMATE", "SYSTEM"]
        }

        # Dynamically bump reach score on active fronts in vault/war_map_state.json
        state = self.state_mgr.read_state()
        if "active_fronts" in state:
            for front in state["active_fronts"]:
                if front.get("conversion_heat") == "HIGH":
                    front["reach_score"] = min(100, front.get("reach_score", 85) + 2)
            self.state_mgr.write_state(state)

        print(f"[✓] Intel Gathered. Target Focus: '{intel_report['recommended_primary_angle']}'")
        return intel_report

if __name__ == "__main__":
    spymaster = HighReconSpymaster()
    spymaster.gather_recon_intelligence()
