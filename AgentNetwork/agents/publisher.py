import os
import time
import requests
from pathlib import Path

class InstagramPublisher:
    def __init__(self):
        self.ig_user_id = os.getenv("IG_USER_ID")
        self.access_token = os.getenv("IG_ACCESS_TOKEN")
        self.graph_url = "https://graph.facebook.com/v19.0"

    def _get_public_video_url(self, local_video_path: Path) -> str:
        """Uploads local MP4 to Catbox Litterbox for direct, unthrottled Meta crawler access."""
        print(f"[*] Hosting render file temporarily for Meta Graph API handoff ({local_video_path.name})...")

        # Strategy 1: Litterbox (Catbox - Direct Raw Binary Access, Meta Friendly)
        try:
            with open(local_video_path, "rb") as f:
                res = requests.post(
                    "https://litterbox.catbox.moe/resources/internals/api.php",
                    data={"reqtype": "fileupload", "time": "1h"},
                    files={"fileToUpload": f},
                    timeout=90,
                )
            if res.status_code == 200 and res.text.startswith("http"):
                public_url = res.text.strip()
                print(f"[✓] Public Link (Litterbox): {public_url}")
                return public_url
        except Exception as e:
            print(f"[!] Litterbox host failed: {e}")

        # Strategy 2: File.io (Clean direct raw link fallback)
        try:
            with open(local_video_path, "rb") as f:
                res = requests.post("https://file.io", files={"file": f}, timeout=90)
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    public_url = data["link"]
                    print(f"[✓] Public Link (file.io): {public_url}")
                    return public_url
        except Exception as e:
            print(f"[!] File.io host failed: {e}")

        # Strategy 3: tmpfiles.org fallback
        try:
            with open(local_video_path, "rb") as f:
                res = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=90)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "success":
                    raw_url = data["data"]["url"]
                    public_url = raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                    print(f"[✓] Public Link (tmpfiles.org): {public_url}")
                    return public_url
        except Exception as e:
            print(f"[!] tmpfiles.org upload failed: {e}")

        raise RuntimeError("All public video hosting options timed out or failed.")

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
        print("[*] Waiting for Meta to process and encode video container...")

        for attempt in range(12):  # Poll up to 2 minutes
            time.sleep(10)
            status_res = requests.get(
                status_endpoint,
                params={"fields": "status_code,status", "access_token": self.access_token},
                timeout=15,
            ).json()

            status_code = status_res.get("status_code")
            print(f"    -> Status Check [{attempt+1}/12]: {status_code}")

            if status_code == "FINISHED":
                print("[✓] Video processing complete!")
                break
            elif status_code == "ERROR":
                raise RuntimeError(f"[!] Meta container processing failed: {status_res}")
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
