import json
from pathlib import Path
from datetime import datetime, timedelta
from AgentNetwork.council.state_manager import StateManager

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PUBLISHED_REELS_PATH = REPO_ROOT / "vault" / "published_reels.json"

class TemporalArchitect:
    def __init__(self):
        self.state_mgr = StateManager()

    def calculate_dispatch_schedule(self) -> dict:
        print("\n=== [TEMPORAL ARCHITECT]: CALCULATING TIMING & DISPATCH SCHEDULE ===")

        state = self.state_mgr.read_state()
        enforcer_status = state.get("system_metrics", {}).get("enforcer_status", "EMERGENCY_PIVOT")

        # Determine frequency based on capital enforcement
        if enforcer_status == "EMERGENCY_PIVOT":
            recommended_interval_hours = 12  # Accelerate output
            dispatch_priority = "IMMEDIATE_STRIKE"
        else:
            recommended_interval_hours = 24  # Standard baseline cadence
            dispatch_priority = "BALANCED_SCHEDULE"

        next_dispatch_time = datetime.utcnow() + timedelta(hours=recommended_interval_hours)

        schedule_plan = {
            "enforcer_status": enforcer_status,
            "dispatch_priority": dispatch_priority,
            "recommended_interval_hours": recommended_interval_hours,
            "next_dispatch_window_utc": next_dispatch_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        print(f"[✓] Schedule Calculated: Priority={dispatch_priority} | Cadence={recommended_interval_hours}h")
        return schedule_plan

if __name__ == "__main__":
    architect = TemporalArchitect()
    architect.calculate_dispatch_schedule()
