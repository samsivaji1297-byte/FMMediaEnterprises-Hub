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

    def get_raw_github_url(self, relative_path: str) -> str:
        """Constructs direct public raw link on GitHub CDN."""
        return f"https://raw.githubusercontent.com/{self.github_repo}/main/MediaFactory/vault/{relative_path}"

    def _generate_fallback_caption(self, base_name: str) -> str:
        """Generates a clean fallback caption if no .txt file exists."""
        clean_title = base_name.replace("_", " ").replace("-", " ").title()
        return (
            f"{clean_title}\n\n"
            "Execution over speculation. Systemize the workflow.\n\n"
            "#automation #productivity #systems #operator #buildinpublic"
        )

    def publish_latest_vault_reel(self) -> str:
        """Processes and publishes the oldest unposted reel from vault queue."""
        if not self.vault_dir.exists():
            print(f"[!] Vault directory does not exist at {self.vault_dir}. No reels to publish.")
            return ""

        queue_file = self.vault_dir / "queue.json"
        posted_runs = []

        if queue_file.exists():
            try:
                with open(queue_file, "r", encoding="utf-8") as f:
                    posted_runs = json.load(f).get("posted", [])
            except Exception:
                posted_runs = []

        # Find target video file across subdirectories or renders/ folder
        target_video_path = None
        target_caption_path = None
        target_run_id = None
        relative_cdn_path = None

        # Check subdirectories first
        subdirs = [d for d in self.vault_dir.iterdir() if d.is_dir()]
        subdirs.sort()

        for d in subdirs:
            if d.name in posted_runs or d.name in ("audio", "renders", "cache"):
                continue
            mp4_file = next((f for f in d.glob("*.mp4")), None)
            if mp4_file:
                target_video_path = mp4_file
                target_caption_path = next((f for f in d.glob("*.txt")), None)
                target_run_id = d.name
                relative_cdn_path = f"{d.name}/{mp4_file.name}"
                break

        # Fallback to direct renders folder if no subfolder run was found
        if not target_video_path:
            renders_dir = self.vault_dir / "renders"
            if renders_dir.exists():
                mp4_files = sorted(renders_dir.glob("*.mp4"))
                for mp4_file in mp4_files:
                    if mp4_file.name not in posted_runs and mp4_file.stem not in posted_runs:
                        target_video_path = mp4_file
                        target_caption_path = mp4_file.with_suffix(".txt")
                        target_run_id = mp4_file.name
                        relative_cdn_path = f"renders/{mp4_file.name}"
                        break

        if not target_video_path:
            print("[*] No pending reels found in vault.")
            return ""

        if not self.access_token or not self.ig_user_id:
            print("[!] Meta API credentials missing in environment variables.")
            return ""

        # Extract or fallback caption text
        caption_text = ""
        if target_caption_path and target_caption_path.exists() and target_caption_path.stat().st_size > 0:
            with open(target_caption_path, "r", encoding="utf-8") as f:
                caption_text = f.read().strip()
            print(f"[✓] Loaded caption from {target_caption_path.name}")
        else:
            caption_text = self._generate_fallback_caption(target_video_path.stem)
            print(f"[*] No caption file found. Applied auto-fallback caption for {target_video_path.name}")

        raw_video_url = self.get_raw_github_url(relative_cdn_path)

        print(f"=== Publishing Reel via Meta Graph API: {target_run_id} ===")
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
            posted_runs.append(target_run_id)
            
            # Ensure folder structure exists for queue writing
            queue_file.parent.mkdir(parents=True, exist_ok=True)
            with open(queue_file, "w", encoding="utf-8") as f:
                json.dump({"posted": posted_runs}, f, indent=4)
                
            print(f"[SUCCESS] Published reel '{target_run_id}' to Instagram! Media ID: {media_id}")
            return media_id

        return ""

if __name__ == "__main__":
    publisher = InstagramPublisher()
    publisher.publish_latest_vault_reel()
