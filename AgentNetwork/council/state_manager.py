import json
import os
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WAR_MAP_STATE_PATH = REPO_ROOT / "vault" / "war_map_state.json"

class StateManager:
    def __init__(self, state_file=WAR_MAP_STATE_PATH):
        self.state_file = Path(state_file)
        self._ensure_state_exists()

    def _ensure_state_exists(self):
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            default_state = {
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
                    "enforcer_status": "RELENTLESS_HUNT"
                },
                "override_instruction": "FORCE_HIGH_CONVERTING_DIRECT_CTA"
            }
            self.write_state(default_state)

    def read_state(self) -> dict:
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error reading state file {self.state_file}: {e}")
            return {}

    def update_metrics(self, daily_conversions: int, enforcer_status: str, override_instruction: str = None):
        """Updates core revenue/war state metrics without overwriting active_fronts or macro_directives."""
        state = self.read_state()
        if "system_metrics" not in state:
            state["system_metrics"] = {}

        state["system_metrics"]["daily_conversions"] = daily_conversions
        state["system_metrics"]["enforcer_status"] = enforcer_status
        if override_instruction:
            state["override_instruction"] = override_instruction

        state["last_updated"] = datetime.utcnow().isoformat()
        self.write_state(state)

    def write_state(self, state_data: dict):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=4)
