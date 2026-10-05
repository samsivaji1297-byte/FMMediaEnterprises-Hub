import os
import time
import subprocess
import requests
from pathlib import Path

class InstagramPublisher:
    def __init__(self):
        self.ig_user_id = os.getenv("IG_USER_ID")
        self.access_token = os.getenv("IG_ACCESS_TOKEN")
        self.graph_url = "https://graph.facebook.com/v19.0"

    def _get_public_video_url(self, local_video_path: Path) -> str:
        """Generates an unthrottled, raw direct media URL for Meta Graph API handoff."""
        print(f"[*] Hosting render file temporarily for Meta Graph API handoff ({local_video_path.name})...")

        # Strategy 1: GitHub Releases / Repo Assets (100% Uptime, Direct CDN, Zero Bot-Blocking)
        try:
            github_token = os.getenv("GITHUB_TOKEN")
            github_repo = os.getenv("GITHUB_REPOSITORY") # e.g. "user/repo"
            
            if github_token and github_repo:
                tag_name = f"render-cache-{int(time.time())}"
                
                # 1. Create temporary release tag
                create_release_cmd = [
                    "gh", "release", "create", tag_name,
                    str(local_video_path),
                    "--title", f"Media Handoff {tag_name}",
                    "--notes", "Temporary video hosting for Meta Graph API crawler",
                    "--repo", github_repo
                ]
                res = subprocess.run(create_release_cmd, capture_output=True, text=True, timeout=60)
                
                if res.returncode == 0:
                    # Construct direct raw GitHub download URL
                    public_url = f"https://github.com/{github_repo}/releases/download/{tag_name}/{local_video_path.name}"
                    print(f"[✓] Public Direct Link (GitHub Release CDN): {public_url}")
                    return public_url
                else:
                    print(f"[!] GH Release create failed: {res.stderr}")
        except Exception as e:
            print(f"[!] GitHub Release strategy failed: {e}")

        # Strategy 2: transfer.sh (Raw byte stream, no WAF challenges)
        try:
            curl_cmd = [
                "curl", "-s", "--upload-file", str(local_video_path),
                f"https://transfer.sh/{local_video_path.name}"
            ]
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=90)
            url = result.stdout.strip()
            if url.startswith("https://transfer.sh/"):
                print(f"[✓] Public Direct Link (transfer.sh): {url}")
                return url
            else:
                print(f"[!] transfer.sh response invalid: {url}")
        except Exception as e:
            print(f"[!] transfer.sh failed: {e}")

        # Strategy 3: bashupload.com (Raw Direct Stream)
        try:
            curl_cmd = [
                "curl", "-s", "-T", str(local_video_path),
                "https://bashupload.com"
            ]
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=90)
            output = result.stdout
            for line in output.splitlines():
                if "wget" in line or "https://bashupload.com/" in line:
                    parts = line.split()
                    for p in parts:
                        if p.startswith("https://bashupload.com/"):
                            print(f"[✓] Public Direct Link (bashupload): {p}")
                            return p
        except Exception as e:
            print(f"[!] bashupload failed: {e}")

        raise RuntimeError("All public video hosting options failed to produce a valid direct URL.")

    def publish_reel(self, video_path: Path, caption: str) -> str:
        """Publishes an MP4 video as an Instagram Reel using Meta Graph API."""
        if not self.ig_user_id or not self.access_token:
            print("[!] Skipping IG publish: IG_USER_ID or IG_ACCESS_TOKEN missing.")
            return ""

        # Step 1: Generate direct HTTPS URL
        video_url = self._get_public_video_url(Path(video_path))

        # Step 2: Create Media Container
        print(f"[*] Initiating IG Reel Media Container creation...")
        container_endpoint = f"{self.graph_url}/{self.ig_user_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token,
        }

        res = requests.post(container_endpoint, data=payload, timeout=30)
        res_data = res.json()

        if "id" not in res_data:
            raise RuntimeError(f"[!] Container creation failed: {res_data}")

        container_id = res_data["id"]
        print(f"[✓] Media Container Created ID: {container_id}")

        # Step 3: Poll Status until FINISHED
        status_endpoint = f"{self.graph_url}/{container_id}"
        print("[*] Waiting 15s for Meta crawler to pull raw media binary...")
        time.sleep(15)

        for attempt in range(15):  # Poll up to 3 minutes
            status_res = requests.get(
                status_endpoint,
                params={"fields": "status_code,status", "access_token": self.access_token},
                timeout=15,
            ).json()

            status_code = status_res.get("status_code")
            print(f"    -> Status Check [{attempt+1}/15]: {status_code}")

            if status_code == "FINISHED":
                print("[✓] Video processing complete!")
                break
            elif status_code == "ERROR":
                raise RuntimeError(f"[!] Meta container processing failed: {status_res}")
            
            time.sleep(10)
        else:
            raise TimeoutError("[!] Meta video container processing timed out.")

        # Step 4: Publish Container
        print("[*] Dispatching publish trigger to Instagram Feed...")
        publish_endpoint = f"{self.graph_url}/{self.ig_user_id}/media_publish"
        publish_res = requests.post(
            publish_endpoint,
            data={"creation_id": container_id, "access_token": self.access_token},
            timeout=30,
        ).json()

        if "id" in publish_res:
            media_id = publish_res["id"]
            print(f"[🔥] SUCCESS! Reel Published Live to Instagram. Media ID: {media_id}")
            return media_id
        else:
            raise RuntimeError(f"[!] IG Media Publish failed: {publish_res}")
