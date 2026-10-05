import os
import time
import json
import requests
from pathlib import Path

class InstagramPublisher:
    """Publishes reels using raw GitHub repository links as the video CDN for Meta Graph API."""

    def __init__(self):
        self.ig_user_id = os.getenv("IG_USER_ID") or os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.access_token = (
            os.getenv("IG_ACCESS_TOKEN")
            or os.getenv("INSTAGRAM_ACCESS_TOKEN")
            or os.getenv("META_ACCESS_TOKEN")
        )
        self.github_repo = os.getenv("GITHUB_REPOSITORY")  # e.g., 'owner/repo'
        self.graph_url = "https://graph.facebook.com/v21.0"
        
        # Path resolution pointing to MediaFactory vault
        self.vault_dir = Path(__file__).resolve().parent.parent.parent / "MediaFactory" / "vault"

    def get_raw_github_url(self, run_folder_name: str, video_filename: str) -> str:
        """Constructs direct public raw link on GitHub CDN."""
        return f"https://raw.githubusercontent.com/{self.github_repo}/main/MediaFactory/vault/{run_folder_name}/{video_filename}"

    def publish_latest_vault_reel(self) -> str:
        """Processes and publishes the oldest unposted reel from vault queue."""
        if not self.vault_dir.exists():
            print(f"[!] Vault directory does not exist at {self.vault_dir}. No reels to publish.")
            return ""

        queue_file = self.vault_dir / "queue.json"
        posted_runs = []

        if queue_file.exists():
            with open(queue_file, "r", encoding="utf-8") as f:
                posted_runs = json.load(f).get("posted", [])

        runs = [d.name for d in self.vault_dir.iterdir() if d.is_dir()]
        runs.sort()  # Process oldest pending reel first

        target_run = next((r for r in runs if r not in posted_runs), None)

        if not target_run:
            print("[*] No pending reels found in vault.")
            return ""

        if not self.access_token or not self.ig_user_id:
            print("[!] Meta API credentials missing in environment variables.")
            return ""

        run_path = self.vault_dir / target_run
        video_file = next((f.name for f in run_path.glob("*.mp4")), None)
        caption_file = next((f.name for f in run_path.glob("*.txt")), None)

        if not video_file or not caption_file:
            print(f"[!] Incomplete vault assets in folder {target_run}.")
            return ""

        with open(run_path / caption_file, "r", encoding="utf-8") as f:
            caption_text = f.read()

        raw_video_url = self.get_raw_github_url(target_run, video_file)

        print(f"=== Publishing Reel via Meta Graph API: {target_run} ===")
        print(f"[*] Public Video URL: {raw_video_url}")

        # Step 1: Create Container
        container_endpoint = f"{self.graph_url}/{self.ig_user_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": raw_video_url,
            "caption": caption_text,
            "access_token": self.access_token,
        }

        res = requests.post(container_endpoint, data=payload, timeout=30).json()
        creation_id = res.get("id")

        if not creation_id:
            print(f"[!] Failed to create container on Meta: {res}")
            return ""

        print(f"[+] Container created! ID: {creation_id}")

        # Step 2: Poll Container Status
        status_endpoint = f"{self.graph_url}/{creation_id}"
        status = ""
        attempts = 0

        while status != "FINISHED" and attempts < 25:
            time.sleep(6)
            status_res = requests.get(
                status_endpoint,
                params={"fields": "status_code", "access_token": self.access_token},
                timeout=15,
            ).json()

            status = status_res.get("status_code", "")
            print(f"[*] Processing status [{attempts + 1}/25]: {status}")

            if status == "FINISHED":
                break
            elif status in ("ERROR", "EXPIRED"):
                print(f"[!] Container processing failed on Meta: {status_res}")
                return ""
            attempts += 1

        if status != "FINISHED":
            print("[!] Media processing timed out on Meta servers.")
            return ""

        # Step 3: Publish Media
        publish_endpoint = f"{self.graph_url}/{self.ig_user_id}/media_publish"
        publish_res = requests.post(
            publish_endpoint,
            data={"creation_id": creation_id, "access_token": self.access_token},
            timeout=15,
        ).json()

        print(f"[+] Publish response: {publish_res}")

        if "id" in publish_res:
            media_id = publish_res["id"]
            posted_runs.append(target_run)
            with open(queue_file, "w", encoding="utf-8") as f:
                json.dump({"posted": posted_runs}, f, indent=4)
            print(f"[SUCCESS] Published reel '{target_run}' to Instagram! Media ID: {media_id}")
            return media_id

        return ""

if __name__ == "__main__":
    publisher = InstagramPublisher()
    publisher.publish_latest_vault_reel()
