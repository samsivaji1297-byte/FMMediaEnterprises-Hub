import os
import json
import requests
import time
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RENDERS_DIR = REPO_ROOT / "MediaFactory" / "vault" / "renders"
QUEUE_FILE = REPO_ROOT / "vault" / "queue.json"
PUBLISHED_FILE = REPO_ROOT / "vault" / "published_reels.json"

class InstagramPublisher:
    def __init__(self):
        self.access_token = os.environ.get("IG_ACCESS_TOKEN") or os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        self.user_id = os.environ.get("IG_USER_ID") or os.environ.get("INSTAGRAM_ACCOUNT_ID")
        self.repo = os.environ.get("GITHUB_REPOSITORY")
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def publish_pending_reels(self):
        print("\n=== [INSTAGRAM PUBLISHER]: DISPATCHING PENDING REELS ===")
        
        if not RENDERS_DIR.exists():
            print(f"[!] Renders directory missing at {RENDERS_DIR}")
            return

        # Find all mp4 files in MediaFactory/vault/renders/
        video_files = list(RENDERS_DIR.glob("*.mp4"))
        if not video_files:
            print("[!] No pending reels found in vault/renders/ directory.")
            return

        published_log = []
        if PUBLISHED_FILE.exists():
            try:
                with open(PUBLISHED_FILE, "r", encoding="utf-8") as f:
                    published_log = json.load(f)
            except Exception:
                published_log = []

        # Build a set of filenames that have already been SUCCESSFULLY published
        already_published = {
            item.get("filename") 
            for item in published_log 
            if isinstance(item, dict) and item.get("status") in ["PUBLISHED", "MOCK_PUBLISHED"]
        }

        for video_path in video_files:
            filename = video_path.name
            
            # If the filename collides with a previously logged entry, generate a unique variant
            if filename in already_published:
                print(f"[!] Warning: '{filename}' already marked as published. Regenerating unique asset signature...")
                unique_suffix = f"_{int(time.time())}_{uuid.uuid4().hex[:4]}"
                new_stem = f"{video_path.stem}{unique_suffix}"
                new_video_path = video_path.with_name(f"{new_stem}.mp4")
                
                # Rename the mp4 file
                video_path.rename(new_video_path)
                
                # Rename associated .txt caption file if present
                txt_path = video_path.with_suffix(".txt")
                if txt_path.exists():
                    new_txt_path = txt_path.with_name(f"{new_stem}.txt")
                    txt_path.rename(new_txt_path)
                
                video_path = new_video_path
                filename = video_path.name
                print(f"[✓] Renamed asset to: '{filename}'")

            txt_path = video_path.with_suffix(".txt")
            caption = ""
            if txt_path.exists():
                caption = txt_path.read_text(encoding="utf-8")

            # CDN URL where GitHub Actions pushed the rendered video asset
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
                continue

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

        # Sync published history back to vault
        PUBLISHED_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PUBLISHED_FILE, "w", encoding="utf-8") as f:
            json.dump(published_log, f, indent=4)

    def _create_container(self, video_url, caption):
        url = f"{self.base_url}/{self.user_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token
        }
        res = requests.post(url, data=payload, timeout=15)
        data = res.json()
        if "error" in data:
            print(f"[!] Container Creation Error: {data['error'].get('message')}")
        return data.get("id")

    def _wait_for_container(self, container_id, max_attempts=12):
        url = f"{self.base_url}/{container_id}?fields=status_code&access_token={self.access_token}"
        for _ in range(max_attempts):
            res = requests.get(url, timeout=10).json()
            status = res.get("status_code")
            if status == "FINISHED":
                return True
            elif status == "ERROR":
                print(f"[!] Meta processing failed for container {container_id}")
                return False
            time.sleep(5)
        return False

    def _publish_container(self, container_id):
        url = f"{self.base_url}/{self.user_id}/media_publish"
        payload = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        res = requests.post(url, data=payload, timeout=15)
        data = res.json()
        if "error" in data:
            print(f"[!] Publish Container Error: {data['error'].get('message')}")
        return data.get("id")

if __name__ == "__main__":
    publisher = InstagramPublisher()
    publisher.publish_pending_reels()
