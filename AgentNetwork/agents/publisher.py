import os
import json
import requests
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RENDERS_DIR = REPO_ROOT / "MediaFactory" / "vault" / "renders"
PUBLISHED_FILE = REPO_ROOT / "vault" / "published_reels.json"

class InstagramPublisher:
    def __init__(self):
        self.access_token = os.environ.get("IG_ACCESS_TOKEN") or os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        self.user_id = os.environ.get("IG_USER_ID") or os.environ.get("INSTAGRAM_ACCOUNT_ID")
        self.repo = os.environ.get("GITHUB_REPOSITORY")
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def publish_pending_reels(self):
        print("\n=== [INSTAGRAM PUBLISHER]: DISPATCHING PENDING REEL (STRICT SINGLETON) ===")
        
        if not RENDERS_DIR.exists():
            print(f"[!] Renders directory missing at {RENDERS_DIR}")
            return

        # Find all MP4 renders in the directory, sorted by modification time (newest first)
        video_files = sorted(RENDERS_DIR.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not video_files:
            print("[!] No pending reels found in vault/renders/ directory.")
            return

        # STRICT SINGLETON ENFORCEMENT: Take ONLY the single newest render file
        target_video_path = video_files[0]
        filename = target_video_path.name
        print(f"[*] Targeting newest singleton render file: {filename}")

        published_log = []
        if PUBLISHED_FILE.exists():
            try:
                with open(PUBLISHED_FILE, "r", encoding="utf-8") as f:
                    published_log = json.load(f)
            except Exception:
                published_log = []

        already_published = {
            item.get("filename") 
            for item in published_log 
            if isinstance(item, dict) and item.get("status") in ["PUBLISHED", "MOCK_PUBLISHED"]
        }

        if filename in already_published:
            print(f"[!] Warning: '{filename}' is already recorded as published. Skipping execution to prevent duplicate publishing.")
            return

        txt_path = target_video_path.with_suffix(".txt")
        caption = ""
        if txt_path.exists():
            caption = txt_path.read_text(encoding="utf-8")

        video_url = f"https://raw.githubusercontent.com/{self.repo}/main/MediaFactory/vault/renders/{filename}"
        print(f"[*] Processing Reel: {filename}")
        print(f"[*] CDN Target URL: {video_url}")

        if not self.access_token or not self.user_id:
            print("[!] IG_ACCESS_TOKEN or IG_USER_ID not configured. Running dry-run mode.")
            published_log.append({
                "filename": filename,
                "media_id": f"mock_id_{filename}",
                "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "status": "MOCK_PUBLISHED"
            })
        else:
            # Verify CDN URL availability before submitting to Meta
            if not self._verify_cdn_url(video_url):
                print(f"[!] CDN URL not yet reachable. Skipping container creation for this cycle.")
                return

            # Meta Graph API Container Creation & Publishing Sequence
            container_id = self._create_container(video_url, caption)
            if container_id and self._wait_for_container(container_id):
                media_id = self._publish_container(container_id)
                if media_id:
                    print(f"[✓] Successfully Published Reel to Instagram! Media ID: {media_id}")
                    published_log.append({
                        "filename": filename,
                        "media_id": media_id,
                        "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "status": "PUBLISHED"
                    })
                else:
                    print("[!] Failed to publish container.")
                    return
            else:
                print("[!] Container processing failed or timed out.")
                return

        PUBLISHED_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PUBLISHED_FILE, "w", encoding="utf-8") as f:
            json.dump(published_log, f, indent=4)
        print(f"[✓] Published log updated successfully.")

    def _verify_cdn_url(self, url: str, max_retries: int = 5, delay: int = 4) -> bool:
        """Verifies that the raw GitHub CDN URL is live and accessible."""
        for attempt in range(1, max_retries + 1):
            try:
                res = requests.head(url, timeout=10)
                if res.status_code == 200:
                    print(f"[✓] CDN URL verified live (Attempt {attempt})")
                    return True
                print(f"[*] CDN returned status {res.status_code}. Waiting for propagation ({attempt}/{max_retries})...")
            except Exception as e:
                print(f"[*] CDN check exception: {e}. Retrying ({attempt}/{max_retries})...")
            time.sleep(delay)
        return False

    def _create_container(self, video_url, caption):
        url = f"{self.base_url}/{self.user_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token
        }
        try:
            res = requests.post(url, data=payload, timeout=20)
            data = res.json()
            if "error" in data:
                print(f"[!] Container Creation Error: {data['error'].get('message')}")
                return None
            return data.get("id")
        except Exception as e:
            print(f"[!] Container creation request failed: {e}")
            return None

    def _wait_for_container(self, container_id, max_attempts=15):
        url = f"{self.base_url}/{container_id}?fields=status_code&access_token={self.access_token}"
        for _ in range(max_attempts):
            try:
                res = requests.get(url, timeout=10).json()
                status = res.get("status_code")
                if status == "FINISHED":
                    return True
                elif status == "ERROR":
                    print(f"[!] Meta processing failed for container {container_id}")
                    return False
            except Exception:
                pass
            time.sleep(6)
        print(f"[!] Container processing timed out for {container_id}")
        return False

    def _publish_container(self, container_id):
        url = f"{self.base_url}/{self.user_id}/media_publish"
        payload = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        try:
            res = requests.post(url, data=payload, timeout=20)
            data = res.json()
            if "error" in data:
                print(f"[!] Publish Container Error: {data['error'].get('message')}")
                return None
            return data.get("id")
        except Exception as e:
            print(f"[!] Publish container request failed: {e}")
            return None

if __name__ == "__main__":
    publisher = InstagramPublisher()
    publisher.publish_pending_reels()
