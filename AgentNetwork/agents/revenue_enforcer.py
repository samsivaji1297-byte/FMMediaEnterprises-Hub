import os
import json
from datetime import datetime

WAR_MAP_STATE = "vault/war_map_state.json"
CONVERSION_LOG = "vault/conversion_log.json"

class RevenueEnforcer:
    def __init__(self, target_daily_conversions=1):
        self.target = target_daily_conversions

    def get_today_conversions(self):
        if not os.path.exists(CONVERSION_LOG):
            return 0
        try:
            with open(CONVERSION_LOG, "r", encoding="utf-8") as f:
                logs = json.load(f)
                today_str = datetime.utcnow().strftime("%Y-%m-%d")
                return sum(1 for log in logs if log.get("date") == today_str and log.get("converted"))
        except Exception as e:
            print(f"[!] Warning reading conversion logs: {e}")
            return 0

    def enforce(self):
        print("=== [REVENUE ENFORCER]: EXECUTING ZERO-TOLERANCE CHECK ===")
        today_conversions = self.get_today_conversions()
        print(f"[*] Current Daily Conversions: {today_conversions} / Target: {self.target}")

        state_data = {}
        if os.path.exists(WAR_MAP_STATE):
            with open(WAR_MAP_STATE, "r", encoding="utf-8") as f:
                state_data = json.load(f)

        if today_conversions < self.target:
            print("[!] STATUS: BELOW TARGET. Triggering Direct-Response Emergency Mode!")
            enforcer_status = "EMERGENCY_PIVOT"
            # Command MediaFactory / Script Generator to use hard-hitting CTA templates
            override_instruction = "FORCE_HIGH_CONVERTING_DIRECT_CTA"
        else:
            print("[+] STATUS: TARGET MET. System operating in Nominal expansion mode.")
            enforcer_status = "NOMINAL"
            override_instruction = "STANDARD_HYBRID_CONTENT"

        # Update global state for War Map & Orchestrator
        if state_data:
            state_data["system_metrics"]["daily_conversions"] = today_conversions
            state_data["system_metrics"]["enforcer_status"] = enforcer_status
            state_data["override_instruction"] = override_instruction
            with open(WAR_MAP_STATE, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=4)

        return {
            "conversions": today_conversions,
            "target": self.target,
            "status": enforcer_status,
            "instruction": override_instruction
        }

if __name__ == "__main__":
    enforcer = RevenueEnforcer(target_daily_conversions=1)
    enforcer.enforce()
