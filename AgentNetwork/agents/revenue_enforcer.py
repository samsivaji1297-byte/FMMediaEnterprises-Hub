import os
import json
from datetime import datetime

STATE_FILE = "vault/war_map_state.json"

class RevenueEnforcer:
    def __init__(self, state_path=STATE_FILE, target_daily_conversions=1, *args, **kwargs):
        self.state_path = state_path
        self.target_daily_conversions = target_daily_conversions

    def load_state(self):
        with open(self.state_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_state(self, state):
        now_iso = datetime.utcnow().isoformat()
        state["last_updated"] = now_iso
        if "system_meta" in state and isinstance(state["system_meta"], dict):
            state["system_meta"]["last_executed"] = now_iso
            
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)

    def enforce(self):
        print("=== [REVENUE ENFORCER]: EXECUTING ZERO-TOLERANCE CHECK ===")
        state = self.load_state()

        # 1. Safely locate KPI structures (dual-schema fallback)
        sovereign_kpis = state.get("sovereign_kpis", {})
        system_metrics = state.get("system_metrics", {})

        # Extract today's conversions with fallbacks across schema versions
        today_conversions = sovereign_kpis.get("conversions_today", system_metrics.get("daily_conversions", 0))
        target_minimum = sovereign_kpis.get("target_minimum", system_metrics.get("target_conversions", self.target_daily_conversions))

        # Safe Log Inspection (handles list of strings or list of dicts)
        execution_log = state.get("execution_log", [])
        for log in execution_log:
            if isinstance(log, dict) and log.get("type") == "conversion":
                today_conversions += 1
            elif isinstance(log, str) and "conversion" in log.lower() and "executed" in log.lower():
                pass 

        print(f"[*] Current Daily Conversions: {today_conversions} / Target: {target_minimum}")

        # 2. Evaluate Target Status
        if today_conversions < target_minimum:
            print("[!] STATUS: BELOW TARGET. Triggering Direct-Response Emergency Mode!")
            mode_status = "DEFICIT // FORCING DIRECT CTA"
            target_status = "UNSATISFIED // FORCING_DIRECT_CTA"
        else:
            print("[+] STATUS: TARGET SATISFIED. Baseline Revenue Secured.")
            mode_status = "SATISFIED // SCALING"
            target_status = "SATISFIED"

        # 3. Safely sync updates back without crashing on missing keys
        if "sovereign_kpis" in state:
            state["sovereign_kpis"]["conversions_today"] = today_conversions
            state["sovereign_kpis"]["target_status"] = target_status

        if "system_metrics" in state:
            state["system_metrics"]["daily_conversions"] = today_conversions

        if "council_telemetry" in state and "MasterOfCoin" in state["council_telemetry"]:
            state["council_telemetry"]["MasterOfCoin"]["mode"] = mode_status

        self.save_state(state)
        print("[+] Revenue enforcement posture updated.")
        return state

if __name__ == "__main__":
    enforcer = RevenueEnforcer()
    enforcer.enforce()
