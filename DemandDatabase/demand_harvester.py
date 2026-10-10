import os
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

DEMAND_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(DEMAND_DIR, "raw_scrapes")
CLUSTERS_FILE = os.path.join(DEMAND_DIR, "keyword_clusters.json")

os.makedirs(RAW_DIR, exist_ok=True)

class DemandHarvester:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    def fetch_search_autocomplete(self, seed_keyword):
        """Mines auto-complete search intent directly from public endpoints."""
        encoded_query = urllib.parse.quote(seed_keyword)
        url = f"http://suggestqueries.google.com/complete/search?output=toolbar&hl=en&q={encoded_query}"
        
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                suggestions = [child.attrib['data'] for child in root.iter('suggestion')]
                return suggestions
        except Exception as e:
            print(f"[!] Error fetching autocomplete for '{seed_keyword}': {e}")
            return []

    def run_harvest_cycle(self, seed_topics):
        """Executes a full upstream harvest cycle, archives history, and updates active clusters."""
        print("=== [DEMAND DATABASE]: HARVESTING UPSTREAM INTENT ===")
        all_clusters = {}
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        for topic in seed_topics:
            print(f"[*] Mining intent for topic: '{topic}'...")
            suggestions = self.fetch_search_autocomplete(topic)
            all_clusters[topic] = {
                "extracted_intents": suggestions,
                "intent_count": len(suggestions),
                "last_scraped": datetime.utcnow().isoformat()
            }

        # 1. Save active latest view for downstream consumption
        with open(CLUSTERS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_clusters, f, indent=4)

        # 2. Archive historical run in raw_scrapes/ for trend tracking
        archive_file = os.path.join(RAW_DIR, f"harvest_{timestamp_str}.json")
        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(all_clusters, f, indent=4)

        print(f"[+] Harvest complete. Active file updated & archived to: {archive_file}")
        return all_clusters

if __name__ == "__main__":
    harvester = DemandHarvester()
    
    # Balanced seeds targeting both execution/automation and psychological readiness
    seeds = [
        # Automation & Systems
        "how to automate * business",
        "ai agents for *",

        # Psychological Readiness & Mindset
        "how to know if ready to *",
        "stop procrastinating on *",
        "overcoming fear of starting *",
        "time management system for entrepreneurs",
        "when to quit day job for *",
        "overcoming hesitation to start building"
    ]
    harvester.run_harvest_cycle(seeds)
