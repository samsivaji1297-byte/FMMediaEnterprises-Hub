import os
import json
from datetime import datetime

DEMAND_DIR = os.path.dirname(os.path.abspath(__file__))
CLUSTERS_FILE = os.path.join(DEMAND_DIR, "keyword_clusters.json")
VAULT_SUMMARY_FILE = os.path.join(os.path.dirname(DEMAND_DIR), "vault", "active_demand_summary.json")

class DemandSynthesizer:
    def __init__(self, clusters_path=CLUSTERS_FILE, output_path=VAULT_SUMMARY_FILE):
        self.clusters_path = clusters_path
        self.output_path = output_path

    def synthesize(self):
        print("=== [DEMAND DATABASE]: SYNTHESIZING DOWNSTREAM AMMUNITION ===")
        
        if not os.path.exists(self.clusters_path):
            print(f"[!] Clusters file not found at {self.clusters_path}")
            return

        with open(self.clusters_path, "r", encoding="utf-8") as f:
            clusters = json.load(f)

        high_priority_intents = []
        
        for seed, data in clusters.items():
            intents = data.get("extracted_intents", [])
            for intent in intents:
                # Filter out pure noise / generic duplicates
                if intent.strip() and intent.lower() != seed.lower():
                    high_priority_intents.append({
                        "source_seed": seed,
                        "intent_phrase": intent,
                        "harvested_at": data.get("last_scraped")
                    })

        summary_payload = {
            "last_synthesized": datetime.utcnow().isoformat(),
            "total_active_intents": len(high_priority_intents),
            "top_demand_angles": high_priority_intents[:15],  # Top 15 actionable angles
            "primary_focus_niche": "Automation, Sovereignty & Execution Readiness"
        }

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(summary_payload, f, indent=4)

        print(f"[+] Active demand summary written to downstream barrier: {self.output_path}")
        return summary_payload

if __name__ == "__main__":
    synthesizer = DemandSynthesizer()
    synthesizer.synthesize()
