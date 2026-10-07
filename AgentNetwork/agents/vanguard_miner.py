import os
import json
import random

QUEUE_PATH = "vault/queue.json"

FRICTION_SEEDS = [
    {
        "hook": "Stop wasting 3 hours every morning organizing messy data.",
        "friction_point": "Manual spreadsheet cleanup and repetitive formatting",
        "solution_cta": "Automate your daily operational workflows in one click."
    },
    {
        "hook": "The biggest friction in your business is back-and-forth scheduling.",
        "friction_point": "Lost hours coordinating calendars and availability",
        "solution_cta": "Eliminate time-sinks with seamless, friction-free booking systems."
    },
    {
        "hook": "If your process relies on manual copy-pasting, you're bleeding revenue.",
        "friction_point": "Disconnected tools and manual input errors",
        "solution_cta": "Build an integrated digital pipeline that runs 24/7."
    }
]

class VanguardMiner:
    def __init__(self, queue_path=QUEUE_PATH):
        self.queue_path = queue_path

    def mine_friction(self):
        print("=== [VANGUARD MINER]: SCRAPING HIGH-FRICTION TARGETS ===")
        selected = random.choice(FRICTION_SEEDS)
        print(f"[+] Friction Isolated: '{selected['friction_point']}'")
        
        # Construct pipeline queue entry
        payload = {
            "title": f"Friction Solution - {selected['friction_point'][:20]}",
            "hook_text": selected["hook"],
            "core_text": f"Daily friction like {selected['friction_point'].lower()} drains energy and halts growth.",
            "cta_text": selected["solution_cta"],
            "broll_query": "office laptop focus dark aesthetic",
            "status": "READY_FOR_RENDER"
        }

        os.makedirs(os.path.dirname(self.queue_path), exist_ok=True)
        queue = []
        if os.path.exists(self.queue_path):
            try:
                with open(self.queue_path, "r", encoding="utf-8") as f:
                    queue = json.load(f)
            except Exception:
                queue = []

        queue.append(payload)
        with open(self.queue_path, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=4)

        print(f"[+] Payload pushed to {self.queue_path}. Queue size: {len(queue)}")
        return payload

if __name__ == "__main__":
    miner = VanguardMiner()
    miner.mine_friction()
