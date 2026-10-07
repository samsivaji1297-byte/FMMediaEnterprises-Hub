import os
import sys
from pathlib import Path

# Ensure repository root is in Python path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from AgentNetwork.council.master_of_coin import MasterOfCoin
from AgentNetwork.council.spymaster import HighReconSpymaster
from AgentNetwork.council.temporal_architect import TemporalArchitect
from AgentNetwork.agents.sales_agent import SalesDMOperator


class WarRoomOrchestrator:
    def __init__(self):
        self.master_of_coin = MasterOfCoin()
        self.spymaster = HighReconSpymaster()
        self.temporal_architect = TemporalArchitect()
        self.sales_operator = SalesDMOperator()

    def execute_campaign_cycle(self):
        print("\n=======================================================")
        print("   [WAR ROOM ORCHESTRATOR]: INITIATING CAMPAIGN CYCLE  ")
        print("=======================================================")

        # Step 1: Capital Audit & State Enforcement
        capital_status = self.master_of_coin.audit_and_enforce_capital()

        # Step 2: Recon Intelligence
        intel_report = self.spymaster.gather_recon_intelligence()

        # Step 3: Timing & Cadence Schedule
        schedule = self.temporal_architect.calculate_dispatch_schedule()

        print("\n-------------------------------------------------------")
        print(f"[*] STRATEGIC STATUS : {capital_status['enforcer_status']}")
        print(f"[*] OVERRIDE MODE    : {capital_status['override_instruction']}")
        print(f"[*] PRIMARY ANGLE    : {intel_report['recommended_primary_angle']}")
        print(f"[*] DISPATCH PRIORITY: {schedule['dispatch_priority']}")
        print("-------------------------------------------------------")

        # Step 4: Sales DM Conversion Sweep
        # Runs sales sweep on recent reels (<72h old, max 5 reels cap)
        self.sales_operator.run_sales_sweep()

        print("\n[✓] WAR ROOM CAMPAIGN CYCLE EXECUTED SUCCESSFULLY.\n")


if __name__ == "__main__":
    orchestrator = WarRoomOrchestrator()
    orchestrator.execute_campaign_cycle()
