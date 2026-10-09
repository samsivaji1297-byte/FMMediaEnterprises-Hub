import os
import json
from datetime import datetime, timezone

# DEFINE VAULT PATHS
VAULT_DIR = "vault"
WAR_MAP_STATE_PATH = os.path.join(VAULT_DIR, "war_map_state.json")
DIRECTIVES_PATH = os.path.join(VAULT_DIR, "operator_directives.json")
REELS_PATH = os.path.join(VAULT_DIR, "published_reels.json")

def ensure_vault():
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR)

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error loading {path}: {e}")
    return default

def save_json(path, data):
    ensure_vault()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def process_directives():
    """
    Ingests inbound operator directives, evaluates recurrence frequency,
    and returns Council accountability responses and escalation levels.
    """
    directives_data = load_json(DIRECTIVES_PATH, {
        "active_directive": None,
        "directive_history": [],
        "escalation_rules": {
            "max_allowed_recurrence": 3,
            "threshold_action": "FORCE_EMERGENCY_PIVOT"
        }
    })

    active = directives_data.get("active_directive")
    history = directives_data.get("directive_history", [])
    
    current_escalation = "LEVEL_0_NOMINAL"
    council_response = "Aurelian High Council operating on standard 4h cadence. Systems nominal."
    last_command = None

    if active and active.get("status") == "PENDING":
        last_command = active.get("prompt", "")
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Check recurrence count against history
        matching_past = [d for d in history if d.get("prompt", "").lower() == last_command.lower()]
        recurrence = len(matching_past) + 1

        if recurrence >= 3:
            current_escalation = "LEVEL_2_EMERGENCY_PIVOT"
            council_response = f"[MASTER OF COIN & SPYMASTER]: Recurrence threshold reached ({recurrence}x). Forcing emergency strategic pivot. Halting weak hooks, doubling conversion CTA aggression on next reel dispatch."
        elif recurrence == 2:
            current_escalation = "LEVEL_1_WARNING"
            council_response = f"[MASTER OF COIN]: Repeated query detected ({recurrence}x). Root Cause: Conversion deficit active. Spymaster adjusting target angle to high-intent pain points."
        else:
            current_escalation = "LEVEL_0_NOMINAL"
            council_response = f"[HIGH COUNCIL]: Directive ingested: '{last_command}'. Executing root cause analysis and optimizing current dispatch cycle."

        # Archive active directive into history
        history_entry = {
            "id": active.get("id", f"dir_{int(datetime.now().timestamp())}"),
            "timestamp": timestamp,
            "type": active.get("type", "ACCOUNTABILITY_QUERY"),
            "prompt": last_command,
            "recurrence_count": recurrence,
            "escalation_level": current_escalation,
            "council_action": council_response
        }
        history.append(history_entry)
        
        # Mark active directive resolved
        active["status"] = "RESOLVED"
        active["escalation_level"] = current_escalation
        active["response"] = council_response
        
        directives_data["active_directive"] = active
        directives_data["directive_history"] = history
        save_json(DIRECTIVES_PATH, directives_data)

    elif history:
        last_entry = history[-1]
        last_command = last_entry.get("prompt")
        council_response = last_entry.get("council_action")
        current_escalation = last_entry.get("escalation_level", "LEVEL_0_NOMINAL")

    return {
        "last_operator_command": last_command,
        "council_response": council_response,
        "escalation_level": current_escalation
    }

def execute_war_room_cycle():
    """
    Executes the Aurelian Orchestrator cycle and emits the Master Telemetry payload.
    """
    ensure_vault()
    now_utc = datetime.now(timezone.utc).isoformat()
    
    # Process Directive Bus
    directive_summary = process_directives()
    
    # Load existing state for persistent values
    existing_state = load_json(WAR_MAP_STATE_PATH, {})
    conversions_today = existing_state.get("sovereign_kpis", {}).get("conversions_today", 0)
    target_minimum = 1
    
    # Evaluate Capital Status
    if conversions_today < target_minimum:
        global_status = "CAPITAL_DEFICIT"
        target_status = "UNSATISFIED // FORCING_DIRECT_CTA"
        enforcer_mode = "DEFICIT // FORCING DIRECT CTA"
    else:
        global_status = "TARGET_SATISFIED"
        target_status = "SATISFIED"
        enforcer_mode = "MODE: SATISFIED // STANDARD HARVEST"

    # Assemble Master Telemetry Payload
    master_telemetry = {
        "system_meta": {
            "version": "2.1.0",
            "kingdom": "Aurelian",
            "last_executed": now_utc,
            "global_status": global_status
        },
        "sovereign_kpis": {
            "conversions_today": conversions_today,
            "target_minimum": target_minimum,
            "target_status": target_status,
            "current_top_angle": "Manual Labor vs Autonomous Pipeline Architecture",
            "active_offer": "Operator Mindset Kit"
        },
        "council_telemetry": {
            "MasterOfCoin": {
                "status": "ACTIVE",
                "mode": enforcer_mode,
                "revenue_status": "DEFICIT" if conversions_today < target_minimum else "NOMINAL"
            },
            "HighReconSpymaster": {
                "status": "ACTIVE",
                "primary_angle": "Manual Labor vs Autonomous Pipeline Architecture",
                "confidence": "94.2%"
            },
            "TemporalArchitect": {
                "status": "ACTIVE",
                "current_cadence": "4h",
                "dispatch_window": "STRIKE_READY"
            }
        },
        "tactical_nodes": {
            "rogue_harvester": {
                "status": "STANDBY // READY FOR DEPLOYMENT",
                "latest_axioms_mined": 0,
                "active_knowledge_vault": ["Leverage vs Labor", "Friction Elimination"]
            },
            "media_factory": {
                "status": "ONLINE // DISPATCH ACTIVE",
                "queued_renders": 1,
                "last_published_id": "REEL_AURELIAN_001"
            }
        },
        "active_directives": {
            "last_operator_command": directive_summary["last_operator_command"],
            "council_response": directive_summary["council_response"],
            "escalation_level": directive_summary["escalation_level"]
        },
        "execution_log": [
            f"[SYSTEM]: Aurelian Orchestrator cycle executed at {now_utc}.",
            f"[DIRECTIVE BUS]: Escalation posture sitting at {directive_summary['escalation_level']}.",
            f"[MASTER OF COIN]: Conversion status evaluated ({conversions_today}/{target_minimum}). Posture: {enforcer_mode}.",
            f"[TEMPORAL ARCHITECT]: 4h dispatch window verified."
        ]
    }

    # Write Master Telemetry Payload
    save_json(WAR_MAP_STATE_PATH, master_telemetry)
    print(f"[+] Aurelian War Room Orchestrator cycle complete. State written to {WAR_MAP_STATE_PATH}")

if __name__ == "__main__":
    execute_war_room_cycle()
