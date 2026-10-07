import os
import json
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path

# Resolve paths relative to repository root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONVERSION_LOG_PATH = REPO_ROOT / "vault" / "conversion_log.json"
PUBLISHED_REELS_PATH = REPO_ROOT / "vault" / "published_reels.json"

# Trigger keyword mapping to specific offer links / direct-response conversion copy
TRIGGER_OFFERS = {
    "PIPELINE": {
        "offer_name": "Digital War Room Architecture Kit",
        "link": "https://gumroad.com/l/your-pipeline-offer",
        "pitch": "Zero fluff. Here is the full multi-agent pipeline architecture and codebase to automate your execution."
    },
    "AUTOMATE": {
        "offer_name": "Sovereign Operator System",
        "link": "https://gumroad.com/l/your-automation-offer",
        "pitch": "Stop manual work. Deploy autonomous scripts that run 24/7 without intervention."
    },
    "SYSTEM": {
        "offer_name": "Execution Codex & Automation Vault",
        "link": "https://gumroad.com/l/your-system-offer",
        "pitch": "The complete operational stack for relentless output and zero-tolerance execution."
    }
}

DEFAULT_OFFER = {
    "offer_name": "War Room Command Vault",
    "link": "https://gumroad.com/l/your-default-offer",
    "pitch": "Access the full autonomous digital war map and high-friction automation tools."
}

class SalesDMOperator:
    def __init__(self):
        self.access_token = os.environ.get("IG_ACCESS_TOKEN") or os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        self.user_id = os.environ.get("IG_USER_ID") or os.environ.get("INSTAGRAM_ACCOUNT_ID")
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def get_active_reels_to_sweep(self, published_log, max_reels=5, active_hours=72):
        """
        STOPGAP FILTER: Only sweeps reels published within the last 72 hours,
        and caps total API calls to a maximum of 5 reels per execution.
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=active_hours)
        active_reels = []

        # Ensure we only evaluate valid dictionary entries
        valid_items = [item for item in published_log if isinstance(item, dict)]

        # Sort so newest published posts come first
        sorted_log = sorted(
            valid_items,
            key=lambda x: x.get("published_at", ""),
            reverse=True
        )

        for item in sorted_log:
            pub_date_str = item.get("published_at")
            if pub_date_str:
                try:
                    # Standard ISO parsing for publication timestamps
                    pub_date = datetime.strptime(pub_date_str, "%Y-%m-%dT%H:%M:%SZ")
                    if pub_date < cutoff_time:
                        continue  # Skip archived reels older than 72 hours
                except ValueError:
                    pass

            active_reels.append(item)
            if len(active_reels) >= max_reels:
                break

        return active_reels

    def run_sales_sweep(self):
        print("\n=== [SALES & DM OPERATOR]: EXECUTING INBOUND CONVERSION SWEEP ===")

        if not self.access_token or not self.user_id:
            print("[!] IG credentials missing in environment. Running simulated DM conversion sweep.")
            self._execute_simulated_sweep()
            return

        # Load published reels to get recent post IDs
        if not PUBLISHED_REELS_PATH.exists():
            print("[!] No published reels found in vault. Skipping live comment sweep.")
            return

        try:
            with open(PUBLISHED_REELS_PATH, "r", encoding="utf-8") as f:
                published = json.load(f)
        except Exception as e:
            print(f"[!] Error loading published reels: {e}")
            return

        # APPLY STOPGAP FILTER: Max 5 reels, published within last 72 hours
        reels_to_sweep = self.get_active_reels_to_sweep(published, max_reels=5, active_hours=72)
        print(f"[*] Stopgap Active: Sweeping {len(reels_to_sweep)} recent reels (Max 5, <72h old).")

        processed_comments = self._load_processed_comments()

        for reel in reels_to_sweep:
            media_id = reel.get("media_id")
            if not media_id or media_id.startswith("mock_"):
                continue

            print(f"[*] Sweeping comments for Reel Media ID: {media_id}")
            comments = self._fetch_media_comments(media_id)

            for comment in comments:
                comment_id = comment.get("id")
                comment_text = comment.get("text", "").upper()
                user = comment.get("from", {})
                username = user.get("username", "Unknown")
                user_id = user.get("id")

                if comment_id in processed_comments:
                    continue

                # Match trigger keywords
                matched_trigger = None
                for keyword in TRIGGER_OFFERS.keys():
                    if keyword in comment_text:
                        matched_trigger = keyword
                        break

                offer = TRIGGER_OFFERS.get(matched_trigger, DEFAULT_OFFER)

                print(f"[+] Friction Trigger Detected from @{username}: '{comment_text}'")
                print(f"[>] Dispatching Direct Response Offer: {offer['offer_name']}")

                # Dispatch Direct Message
                dm_success = self._send_direct_message(user_id, username, offer)
                
                # Log conversion event
                self._log_conversion_event(
                    username=username,
                    trigger=matched_trigger or "DIRECT_ENGAGEMENT",
                    offer_name=offer["offer_name"],
                    status="DM_DISPATCHED" if dm_success else "DM_FAILED"
                )

                processed_comments.append(comment_id)

        self._save_processed_comments(processed_comments)

    def _fetch_media_comments(self, media_id):
        url = f"{self.base_url}/{media_id}/comments"
        params = {
            "fields": "id,text,from,timestamp",
            "access_token": self.access_token
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                return res.json().get("data", [])
        except Exception as e:
            print(f"[!] Failed to fetch comments for {media_id}: {e}")
        return []

    def _send_direct_message(self, user_id, username, offer):
        """Dispatches automated direct-response message via Meta Messaging API."""
        message_text = (
            f"No fluff. You requested the friction-strike protocol.\n\n"
            f"► Offer: {offer['offer_name']}\n"
            f"► Focus: {offer['pitch']}\n\n"
            f"Access link: {offer['link']}\n\n"
            f"Execute immediately."
        )

        url = f"{self.base_url}/me/messages"
        payload = {
            "recipient": {"id": user_id},
            "message": {"text": message_text},
            "access_token": self.access_token
        }
        try:
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                print(f"[✓] Direct Response DM delivered to @{username}")
                return True
            else:
                print(f"[!] Meta DM endpoint response ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"[!] DM dispatch error to @{username}: {e}")
        return False

    def _execute_simulated_sweep(self):
        """Simulates conversion sweep in dry-run mode to maintain pipeline continuity."""
        print("[*] Simulating conversion sweep for active leads...")
        self._log_conversion_event(
            username="Operator_Inbound",
            trigger="PIPELINE",
            offer_name=TRIGGER_OFFERS["PIPELINE"]["offer_name"],
            status="MOCK_CONVERTED"
        )

    def _log_conversion_event(self, username, trigger, offer_name, status):
        CONVERSION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        log_data = {
            "conversions": [],
            "processed_comments": []
        }

        if CONVERSION_LOG_PATH.exists():
            try:
                with open(CONVERSION_LOG_PATH, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
            except Exception:
                pass

        if "conversions" not in log_data:
            log_data["conversions"] = []

        log_data["conversions"].append({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "username": username,
            "trigger_keyword": trigger,
            "offer": offer_name,
            "status": status
        })

        with open(CONVERSION_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=4)
        print(f"[+] Conversion state updated in {CONVERSION_LOG_PATH}")

    def _load_processed_comments(self):
        if CONVERSION_LOG_PATH.exists():
            try:
                with open(CONVERSION_LOG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("processed_comments", [])
            except Exception:
                return []
        return []

    def _save_processed_comments(self, processed_comments):
        log_data = {}
        if CONVERSION_LOG_PATH.exists():
            try:
                with open(CONVERSION_LOG_PATH, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
            except Exception:
                pass
        log_data["processed_comments"] = processed_comments
        with open(CONVERSION_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=4)

if __name__ == "__main__":
    operator = SalesDMOperator()
    operator.run_sales_sweep()
