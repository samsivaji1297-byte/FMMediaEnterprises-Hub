import os
import time
import requests
from pathlib import Path

ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

def get_reel_public_url(video_path: Path) -> str:
    repo_name = os.getenv("GITHUB_REPOSITORY", "samsivaji1297-byte/FMMediaEnterprises-Hub")
    branch = "main"
    relative_path = f"ContentFactory/reels/output/{video_path.name}"
    return f"https://raw.githubusercontent.com/{repo_name}/{branch}/{relative_path}"

def ensure_url_accessible(url: str, max_retries: int = 12, delay: int = 5):
    print(f"Verifying public availability of CDN video URL: {url}")
    for attempt in range(1, max_retries + 1):
        try:
            res = requests.head(url, timeout=10)
            if res.status_code == 200 and int(res.headers.get("Content-Length", 0)) > 1000:
                print("CDN URL verified and ready for Meta ingestion.")
                return True
        except Exception:
            pass
        print(f"Waiting for GitHub CDN propagation... (Attempt {attempt}/{max_retries})")
        time.sleep(delay)
    raise TimeoutError(f"Video URL failed to propagate on GitHub CDN: {url}")

def wait_for_reel_ready(creation_id: str, max_attempts: int = 15, delay_seconds: int = 10):
    status_url = f"https://graph.facebook.com/v19.0/{creation_id}"
    params = {"fields": "status_code,status", "access_token": ACCESS_TOKEN}
    
    for attempt in range(1, max_attempts + 1):
        res = requests.get(status_url, params=params).json()
        status_code = res.get("status_code")
        if status_code == "FINISHED":
            print("Meta Reel processing completed successfully.")
            return True
        elif status_code == "ERROR":
            raise Exception(f"Meta Reel processing failed: {res}")
        print(f"Meta Reel container processing... ({attempt}/{max_attempts})")
        time.sleep(delay_seconds)
    raise TimeoutError("Reel container processing timed out on Meta servers.")

def publish_reel_to_ig():
    if not ACCESS_TOKEN or not IG_USER_ID:
        raise ValueError("IG_ACCESS_TOKEN or IG_USER_ID environment variables are missing.")

    video_path = Path(__file__).parent / "output" / "output-reel.mp4"
    if not video_path.exists():
        raise FileNotFoundError(f"Reel video file not found at: {video_path}")

    video_url = get_reel_public_url(video_path)
    ensure_url_accessible(video_url)

    container_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    
    # Tailored caption highlighting operational compression, operator frameworks, and automated leverage
    caption = (
        "Most people trade hours for manual busywork instead of building systems that run themselves. "
        "The Operator Mindset is about compressing hours of repetitive tasks into bulletproof automated pipelines.\n\n"
        "Comment **FM** below and I'll instantly send you the complete framework protocol link.\n\n"
        "#OperatorMindset #TheCompressionSystem #BusinessAutomation #DigitalLeverage #SovereignSystems #WorkflowAutomation"
    )
    
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    
    print("Initiating Meta Reel container creation...")
    response = requests.post(container_url, data=payload).json()
    if "id" not in response:
        raise Exception(f"Failed to create Reel container: {response}")

    creation_id = response["id"]
    wait_for_reel_ready(creation_id)

    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    publish_payload = {"creation_id": creation_id, "access_token": ACCESS_TOKEN}
    
    publish_response = requests.post(publish_url, data=publish_payload).json()
    if "id" not in publish_response:
        raise Exception(f"Failed to publish Reel: {publish_response}")

    published_media_id = publish_response['id']
    print(f"Successfully published Instagram Reel! Post ID: {published_media_id}")

    # Post automated engagement comment driving the "Comment FM" loop
    comment_url = f"https://graph.facebook.com/v19.0/{published_media_id}/comments"
    comment_payload = {
        "message": "Comment FM below and I will DM you the compression system link.",
        "access_token": ACCESS_TOKEN
    }
    
    comment_response = requests.post(comment_url, data=comment_payload).json()
    if "id" in comment_response:
        print(f"Successfully posted engagement comment! Comment ID: {comment_response['id']}")

if __name__ == "__main__":
    publish_reel_to_ig()
