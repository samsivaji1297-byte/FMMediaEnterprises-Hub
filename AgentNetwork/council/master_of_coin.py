import os
import json
from pathlib import Path
from datetime import datetime
from AgentNetwork.council.state_manager import StateManager

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONVERSION_LOG_PATH = REPO_ROOT / "vault" / "conversion_log.json"

class MasterOfCoin:
    def __init__(self, target_conversions=1):
        self.state_mgr = StateManager()
        self.target_conversions = target_conversions

    def audit_and_enforce_capital(self) -> dict:
        print("\n=== [MASTER OF COIN]: AUDITING DAILY CAPITAL & CONVERSION HARVEST ===")
        
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        conversions_today = 0

        # Read actual conversion logs from sales sweeps
        if CONVERSION_LOG_PATH.exists():
            try:
                with open(CONVERSION_LOG_PATH, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
                    conversions = log_data.get("conversions", [])
                    
                    conversions_today = sum(
                        1 for conv in conversions 
                        if isinstance(conv, dict) 
                        and conv.get("timestamp", "").startswith(today_str)
                        and conv.get("status") in ["DM_DISPATCHED", "MOCK_CONVERTED", "CONVERTED"]
                    )
            except Exception as e:
                print(f"[!] Warning reading conversion log: {e}")

        target_met = conversions_today >= self.target_conversions

        if target_met:
            enforcer_status = "BASELINE_STABLE"
            override_instruction = "MAINTAIN_BALANCED_CONTENT_MIX"
            print(f"[✓] CAPITAL TARGET MET ({conversions_today}/{self.target_conversions}). Operating in baseline growth mode.")
        else:
            enforcer_status = "EMERGENCY_PIVOT"
            override_instruction = "FORCE_HIGH_CONVERTING_DIRECT_CTA"
            print(f"[!] CAPITAL TARGET UNSATISFIED ({conversions_today}/{self.target_conversions}). Forcing high-friction direct CTAs across all content!")

        # Sync back into vault/war_map_state.json
        self.state_mgr.update_metrics(
            daily_conversions=conversions_today,
            enforcer_status=enforcer_status,
            override_instruction=override_instruction
        )

        return {
            "conversions_today": conversions_today,
            "target": self.target_conversions,
            "enforcer_status": enforcer_status,
            "override_instruction": override_instruction
        }

if __name__ == "__main__":
    moc = MasterOfCoin()
    moc.audit_and_enforce_capital()
