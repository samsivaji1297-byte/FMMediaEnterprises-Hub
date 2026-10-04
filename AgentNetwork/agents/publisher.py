import time
import requests
import json
from pathlib import Path
from AgentNetwork.config.settings import IG_USER_ID, IG_ACCESS_TOKEN, QUEUE_FILE
from AgentNetwork.core.schemas import ScriptPayload

class PublisherAgent:
    def __init__(self):
        self.user_id = IG_USER_ID
        self.access_token = IG_ACCESS_TOKEN
        self.api_version = "v20.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def publish_reel(self, video_url: str, script: ScriptPayload) -> str:
        """Publishes container to Instagram Reels and tracks permalink."""
        if not self.user_id or not self.access_token:
            raise ValueError("Missing Instagram API credentials in settings/env.")

        caption = f"{script.hook_text}\n\n{' '.join(script.body_points)}\n\n{script.call_to_action}"
        
        # Step 1: Create Container
        container_url = f"{self.base_url}/{self.user_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token
        }
        res = requests.post(container_url, data=payload).json()
        container_id = res.get("id")

        if not container_id:
            raise RuntimeError(f"Failed to create IG media container: {res}")

        # Step 2: Poll Container Status
        status_url = f"{self.base_url}/{container_id}"
        print(f"[*] Processing Reel Container ID: {container_id}...")
        
        for _ in range(12):  # Poll up to 60 seconds
            time.sleep(5)
            status_res = requests.get(status_url, params={"fields": "status_code", "access_token": self.access_token}).json()
            status = status_res.get("status_code")
            if status == "FINISHED":
                break
            elif status == "ERROR":
                raise RuntimeError(f"IG Media container processing error: {status_res}")

        # Step 3: Publish Media
        publish_url = f"{self.base_url}/{self.user_id}/media_publish"
        pub_res = requests.post(publish_url, data={"creation_id": container_id, "access_token": self.access_token}).json()
        media_id = pub_res.get("id")

        # Step 4: Fetch Direct Permalink
        permalink_res = requests.get(
            f"{self.base_url}/{media_id}",
            params={"fields": "permalink", "access_token": self.access_token}
        ).json()
        
        permalink = permalink_res.get("permalink", "N/A")
        print(f"[✓] Live on Instagram: {permalink}")

        # Step 5: Log Record
        self._record_publication(media_id, permalink, script)
        return permalink

    def _record_publication(self, media_id: str, permalink: str, script: ScriptPayload):
        queue = []
        if QUEUE_FILE.exists():
            with open(QUEUE_FILE, "r") as f:
                try:
                    queue = json.load(f)
                except Exception:
                    queue = []

        queue.append({
            "media_id": media_id,
            "permalink": permalink,
            "title": script.title,
            "theme": script.theme,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "metrics": {"plays": 0, "reach": 0, "shares": 0, "saves": 0}
        })

        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2)
