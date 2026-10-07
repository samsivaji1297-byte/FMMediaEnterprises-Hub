import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INTELLIGENCE_FILE = REPO_ROOT / "vault" / "intelligence.json"
PUBLISHED_LOG = REPO_ROOT / "vault" / "published_reels.json"

class InstagramAnalyticsAgent:
    def __init__(self):
        self.access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        self.instagram_account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID")
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def fetch_media_metrics(self, media_id: str):
        """Fetches reach, plays, saves, and share counts for a specific Reel."""
        if not self.access_token:
            print("[!] INSTAGRAM_ACCESS_TOKEN not set. Running in dry-run mode.")
            return self._generate_mock_metrics(media_id)

        metrics = "plays,reach,saved,shares,total_interactions"
        url = f"{self.base_url}/{media_id}/insights?metric={metrics}&access_token={self.access_token}"

        try:
            res = requests.get(url, timeout=10)
            data = res.json()
            
            if "data" not in data:
                print(f"[!] Error pulling metrics for {media_id}: {data}")
                return None

            results = {}
            for item in data.get("data", []):
                name = item.get("name")
                value = item.get("values", [{}])[0].get("value", 0)
                results[name] = value

            return results
        except Exception as e:
            print(f"[!] Network error fetching analytics for {media_id}: {e}")
            return None

    def _generate_mock_metrics(self, media_id: str):
        """Simulates response when running in local development without live API keys."""
        import random
        return {
            "plays": random.randint(800, 12000),
            "reach": random.randint(600, 9500),
            "saved": random.randint(15, 340),
            "shares": random.randint(10, 210),
            "total_interactions": random.randint(30, 600)
        }

    def update_intelligence(self):
        """Processes published media, updates performance scores, and trains intelligence memory."""
        print("\n=== [INSTAGRAM ANALYTICS AGENT]: SCRAPING PERFORMANCE DATA ===")

        if not PUBLISHED_LOG.exists():
            print("[!] No published_reels.json found in vault. Skipping analytics sweep.")
            return

        with open(PUBLISHED_LOG, "r", encoding="utf-8") as f:
            published_items = json.load(f)

        intelligence_data = {
            "last_analytics_run": datetime.utcnow().isoformat(),
            "top_performing_hooks": [],
            "underperforming_hooks": [],
            "aggregate_stats": {"total_plays": 0, "total_saves": 0, "total_shares": 0}
        }

        if INTELLIGENCE_FILE.exists():
            try:
                with open(INTELLIGENCE_FILE, "r", encoding="utf-8") as f:
                    intelligence_data.update(json.load(f))
            except Exception:
                pass

        for item in published_items:
            media_id = item.get("media_id")
            hook_text = item.get("hook_text", "Unknown Hook")
            
            if not media_id:
                continue

            metrics = self.fetch_media_metrics(media_id)
            if not metrics:
                continue

            plays = metrics.get("plays", 0)
            saves = metrics.get("saved", 0)
            shares = metrics.get("shares", 0)

            # Calculate Capital Efficiency Index (CEI) / Engagement Ratio
            # Saves & Shares carry 3x weight (indicates viral/friction value)
            engagement_score = (plays * 0.1) + (saves * 3.0) + (shares * 3.0)

            intelligence_data["aggregate_stats"]["total_plays"] += plays
            intelligence_data["aggregate_stats"]["total_saves"] += saves
            intelligence_data["aggregate_stats"]["total_shares"] += shares

            entry = {
                "media_id": media_id,
                "hook": hook_text,
                "plays": plays,
                "saves": saves,
                "shares": shares,
                "score": round(engagement_score, 2)
            }

            # Classify High vs Underperforming
            if engagement_score > 300 and entry not in intelligence_data["top_performing_hooks"]:
                intelligence_data["top_performing_hooks"].append(entry)
            elif engagement_score < 50 and entry not in intelligence_data["underperforming_hooks"]:
                intelligence_data["underperforming_hooks"].append(entry)

            print(f"[✓] Scraped Reel {media_id} | Plays: {plays} | Saves: {saves} | Score: {round(engagement_score, 2)}")

        # Persist updated memory
        INTELLIGENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(INTELLIGENCE_FILE, "w", encoding="utf-8") as f:
            json.dump(intelligence_data, f, indent=4)

        print(f"[+] Closed-loop memory synchronized to {INTELLIGENCE_FILE}")

if __name__ == "__main__":
    agent = InstagramAnalyticsAgent()
    agent.update_intelligence()
