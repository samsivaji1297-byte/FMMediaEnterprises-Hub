import os
import json
import time
from datetime import datetime

STATE_FILE = "vault/war_map_state.json"

class GrandStrategist:
    def __init__(self, state_path=STATE_FILE):
        self.state_path = state_path
        self.ensure_state_exists()

    def ensure_state_exists(self):
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        if not os.path.exists(self.state_path):
            initial_state = {
                "system_meta": {
                    "version": "2.1.0",
                    "kingdom": "Aurelian",
                    "last_executed": datetime.utcnow().isoformat(),
                    "global_status": "CAPITAL_DEFICIT"
                },
                "last_updated": datetime.utcnow().isoformat(),
                "macro_directives": [
                    "Monetize high-frequency operational time-sinks",
                    "Expand visual reach via dynamic B-roll and kinetic safe-zone text",
                    "Maintain zero-tolerance daily conversion baseline"
                ],
                "active_fronts": [
                    {
                        "id": "front_01",
                        "name": "Time-Sinks & Friction",
                        "status": "ENGAGED",
                        "target_niche": "Automation / Productivity",
                        "reach_score": 85,
                        "conversion_heat": "HIGH"
                    },
                    {
                        "id": "front_02",
                        "name": "Mindset & Sovereignty",
                        "status": "EXPANDING",
                        "target_niche": "Personal Sovereignty / Operator Mindset",
                        "reach_score": 70,
                        "conversion_heat": "MEDIUM"
                    }
                ],
                "system_metrics": {
                    "total_content_rendered": 0,
                    "daily_conversions": 0,
                    "target_conversions": 1,
                    "enforcer_status": "NOMINAL"
                }
            }
            self.save_state(initial_state)

    def load_state(self):
        with open(self.state_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_state(self, state):
        now_iso = datetime.utcnow().isoformat()
        
        # Keep both top-level and nested system_meta timestamps in sync
        state["last_updated"] = now_iso
        if "system_meta" in state and isinstance(state["system_meta"], dict):
            state["system_meta"]["last_executed"] = now_iso
            
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)

    def evaluate_strategy(self):
        state = self.load_state()
        print("=== [GRAND STRATEGIST]: EVALUATING WAR MAP ===")
        
        # 1. Safe Last State Update extraction
        system_meta = state.get('system_meta', {})
        last_updated = system_meta.get('last_executed', state.get('last_updated', 'N/A'))
        print(f"[*] Last State Update: {last_updated}")
        
        # 2. Safe Directives extraction
        directives = state.get('macro_directives', state.get('active_directives', []))
        if isinstance(directives, dict):
            directive_count = len(directives)
        elif isinstance(directives, list):
            directive_count = len(directives)
        else:
            directive_count = 0
        print(f"[*] Active Directives: {directive_count}")
        
        # 3. Safe Active Fronts / Tactical Nodes extraction
        fronts = state.get('active_fronts', state.get('tactical_nodes', []))
        if isinstance(fronts, dict):
            front_count = len(fronts)
        elif isinstance(fronts, list):
            front_count = len(fronts)
        else:
            front_count = 0
        print(f"[*] Active Fronts / Nodes Engaged: {front_count}")
        
        # Grand Strategist updates campaign priorities safely
        self.save_state(state)
        print("[+] Strategy state synchronized successfully.")
        return state

if __name__ == "__main__":
    strategist = GrandStrategist()
    strategist.evaluate_strategy()
