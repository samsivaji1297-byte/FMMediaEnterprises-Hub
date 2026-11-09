import os
import time
import requests
from pathlib import Path

ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

def get_reel_public_url(video_path: Path) -> str:
    """Generates raw GitHub CDN URL for the recorded video asset."""
    repo_name = os.getenv("GITHUB_REPOSITORY", "samsivaji1297-byte/FMMediaEnterprises-Hub")
    branch = "main"
    relative_path = f"ContentFactory/reels/output/{video_path.name}"
    raw_url = f"https://raw.githubusercontent.com/{repo_name}/{branch}/{relative_path}"
    print(f"Using public Reel URL for Meta API: {raw_url}")
    return raw_url

def wait_for_reel_ready(creation_id: str, max_attempts: int = 12, delay_seconds: int = 10):
    """Polls Meta Graph API until the Reel container status is FINISHED."""
    status_url = f"https://graph.facebook.com/v19.0/{creation_id}"
    params = {
        "fields": "status_code,status",
        "access_token": ACCESS_TOKEN
    }
    
    print(f"Polling status for Reel container {creation_id}...")
    for attempt in range(1, max_attempts + 1):
        res = requests.get(status_url, params=params).json()
        status_code = res.get("status_code")
        print(f"Attempt {attempt}/{max_attempts}: Reel status_code is '{status_code}'")
        
        if status_code == "FINISHED":
            print("Reel container processing FINISHED. Ready to publish.")
            return True
        elif status_code == "ERROR":
            raise Exception(f"Meta Reel processing failed: {res}")
        
        time.sleep(delay_seconds)
        
    raise TimeoutError(f"Reel container {creation_id} was not ready within timeout.")

def publish_reel_to_ig():
    if not ACCESS_TOKEN or not IG_USER_ID:
        raise ValueError("IG_ACCESS_TOKEN or IG_USER_ID environment variables are missing.")

    video_path = Path(__file__).parent / "output" / "output-reel.webm"
    if not video_path.exists():
        raise FileNotFoundError(f"Reel video file not found at: {video_path}")

    video_url = get_reel_public_url(video_path)

    # Step 1: Create REELS media container
    container_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    caption = (
        "What was once manual is now fully automated in 90 minutes. "
        "Here is the architectural reality.\n\n"
        "Explore the full operational protocol at fmframeworks.gumroad.com\n\n"
        "#TheCompressionSystem #DigitalProducts #SystemArchitect #Automation"
    )
    
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    
    response = requests.post(container_url, data=payload).json()
    if "id" not in response:
        raise Exception(f"Failed to create Reel container: {response}")

    creation_id = response["id"]
    print(f"Reel container created: {creation_id}.")

    # Step 2: Poll status until Meta finishes processing the video file
    wait_for_reel_ready(creation_id)

    # Step 3: Publish Reel container
    print("Publishing Reel to feed...")
    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }
    
    publish_response = requests.post(publish_url, data=publish_payload).json()
    if "id" not in publish_response:
        raise Exception(f"Failed to publish Reel: {publish_response}")

    published_media_id = publish_response['id']
    print(f"Successfully published Instagram Reel! Post ID: {published_media_id}")

    # Step 4: Drop generic automated FM comment
    comment_url = f"https://graph.facebook.com/v19.0/{published_media_id}/comments"
    comment_payload = {
        "message": "FM — Full operational protocol & sovereign frameworks available at fmframeworks.gumroad.com",
        "access_token": ACCESS_TOKEN
    }
    
    comment_response = requests.post(comment_url, data=comment_payload).json()
    if "id" in comment_response:
        print(f"Successfully posted automated comment! Comment ID: {comment_response['id']}")
    else:
        print(f"Warning: Failed to post comment: {comment_response}")

if __name__ == "__main__":
    publish_reel_to_ig()
