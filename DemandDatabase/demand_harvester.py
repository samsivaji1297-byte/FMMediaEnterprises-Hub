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

    def fetch_forum_friction(self, query, limit=5):
        """Queries public discussion threads for raw human language & friction."""
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}+site:reddit.com"
        
        # Returns parsed intent seeds
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')
                # Minimal snippet extraction logic
                return {"query": query, "raw_length": len(html), "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            print(f"[!] On-demand search failed for '{query}': {e}")
            return {}

    def run_harvest_cycle(self, seed_topics):
        """Executes a full upstream harvest cycle and updates keyword_clusters.json."""
        print("=== [DEMAND DATABASE]: HARVESTING UPSTREAM INTENT ===")
        all_clusters = {}

        for topic in seed_topics:
            print(f"[*] Mining intent for topic: '{topic}'...")
            suggestions = self.fetch_search_autocomplete(topic)
            all_clusters[topic] = {
                "extracted_intents": suggestions,
                "intent_count": len(suggestions),
                "last_scraped": datetime.utcnow().isoformat()
            }

        # Save raw output inside demanddatabase/
        with open(CLUSTERS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_clusters, f, indent=4)

        print(f"[+] Demand harvest complete. Seed clusters saved to: {CLUSTERS_FILE}")
        return all_clusters

if __name__ == "__main__":
    harvester = DemandHarvester()
    # Initial evergreen seed topics
    seeds = [
        "how to automate my business",
        "how do i know if im ready to start",
        "time management template for founders",
        "ai agents for sales"
    ]
    harvester.run_harvest_cycle(seeds)
