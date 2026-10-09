import os
import json
from datetime import datetime, timezone

VAULT_DIR = "vault"
WAR_MAP_STATE_PATH = os.path.join(VAULT_DIR, "war_map_state.json")
HARVEST_VAULT_PATH = os.path.join(VAULT_DIR, "rogue_harvest_vault.json")

def ensure_vault():
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR)

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Harvester load error ({path}): {e}")
    return default

def save_json(path, data):
    ensure_vault()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class RogueHarvester:
    """
    Rogue Harvester Node (Asymmetric Value Extractor)
    Hunts, strips, and distills raw conceptual frameworks into 1-line high-yielding value axioms.
    """
    def __init__(self):
        ensure_vault()
        self.harvest_db = load_json(HARVEST_VAULT_PATH, {
            "node_status": "ONLINE",
            "last_harvest_timestamp": None,
            "mined_axioms": [
                {
                    "id": "ax_001",
                    "source": "Leverage Codex",
                    "axiom": "Stop selling time in hours; sell the automated elimination of operational friction.",
                    "hook_angle": "Manual Labor vs Autonomous Pipeline Architecture",
                    "yield_score": 0.96
                },
                {
                    "id": "ax_002",
                    "source": "Sovereign Circuit",
                    "axiom": "Complexity is the refuge of non-executors. Zero-friction speed is sovereign.",
                    "hook_angle": "Zero-Friction Execution Protocols",
                    "yield_score": 0.92
                }
            ]
        })

    def run_harvest_cycle(self, raw_input_text=None):
        now_utc = datetime.now(timezone.utc).isoformat()
        
        if raw_input_text:
            distilled_axiom = {
                "id": f"ax_{int(datetime.now().timestamp())}",
                "source": "Operator Manual Ingest",
                "axiom": raw_input_text.strip(),
                "hook_angle": "Direct Value Extraction",
                "yield_score": 0.95
            }
            self.harvest_db["mined_axioms"].append(distilled_axiom)

        self.harvest_db["last_harvest_timestamp"] = now_utc
        self.harvest_db["node_status"] = "ONLINE // HARVEST_ACTIVE"
        save_json(HARVEST_VAULT_PATH, self.harvest_db)

        # Update tactical_nodes inside war_map_state.json
        war_state = load_json(WAR_MAP_STATE_PATH, {})
        if "tactical_nodes" not in war_state:
            war_state["tactical_nodes"] = {}

        top_axioms = [a["axiom"] for a in self.harvest_db["mined_axioms"][-3:]]

        war_state["tactical_nodes"]["rogue_harvester"] = {
            "status": "ONLINE // HARVEST_ACTIVE",
            "latest_axioms_mined": len(self.harvest_db["mined_axioms"]),
            "active_knowledge_vault": top_axioms,
            "last_sync": now_utc
        }

        if "execution_log" in war_state:
            war_state["execution_log"].append(
                f"[ROGUE HARVESTER]: Mined & verified {len(self.harvest_db['mined_axioms'])} high-yield value axioms."
            )

        save_json(WAR_MAP_STATE_PATH, war_state)
        print(f"[+] Rogue Harvester cycle complete. {len(self.harvest_db['mined_axioms'])} axioms active.")
        return top_axioms

if __name__ == "__main__":
    harvester = RogueHarvester()
    harvester.run_harvest_cycle()
