import os
import time
import requests
from pathlib import Path

# Meta Graph API Credentials from GitHub Secrets
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

def upload_image_to_hosting(image_path: Path) -> str:
    """Uses the repository's raw GitHub CDN URL for Meta API container consumption."""
    repo_name = os.getenv("GITHUB_REPOSITORY", "samsivaji1297-byte/FMMediaEnterprises-Hub")
    branch = "main"
    relative_path = f"ContentFactory/carousel/{image_path.name}"
    raw_url = f"https://raw.githubusercontent.com/{repo_name}/{branch}/{relative_path}"
    print(f"Using public asset URL for Meta API: {raw_url}")
    return raw_url

def wait_for_container_ready(creation_id: str, max_attempts: int = 10, delay_seconds: int = 5):
    """Polls Meta Graph API until the carousel media container status is FINISHED."""
    status_url = f"https://graph.facebook.com/v19.0/{creation_id}"
    params = {
        "fields": "status_code,status",
        "access_token": ACCESS_TOKEN
    }
    
    print(f"Polling status for media container {creation_id}...")
    for attempt in range(1, max_attempts + 1):
        res = requests.get(status_url, params=params).json()
        status_code = res.get("status_code")
        print(f"Attempt {attempt}/{max_attempts}: Container status_code is '{status_code}'")
        
        if status_code == "FINISHED":
            print("Media container processing FINISHED. Ready to publish.")
            return True
        elif status_code == "ERROR":
            raise Exception(f"Meta media processing failed: {res}")
        
        time.sleep(delay_seconds)
        
    raise TimeoutError(f"Container {creation_id} was not ready within {max_attempts * delay_seconds} seconds.")

def publish_carousel_to_ig():
    if not ACCESS_TOKEN or not IG_USER_ID:
        raise ValueError("IG_ACCESS_TOKEN or IG_USER_ID environment variables are missing.")

    output_dir = Path(__file__).parent
    slide_images = sorted(list(output_dir.glob("output-slide-*.png")))
    
    if not slide_images:
        raise FileNotFoundError("No rendered carousel slides found to publish.")

    print(f"Found {len(slide_images)} slides to publish as an Instagram carousel.")
    
    # Step 1: Create item containers for each slide
    child_container_ids = []
    for img_path in slide_images:
        image_url = upload_image_to_hosting(img_path)
        
        item_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
        payload = {
            "image_url": image_url,
            "is_carousel_item": "true",
            "access_token": ACCESS_TOKEN
        }
        response = requests.post(item_url, data=payload).json()
        if "id" not in response:
            raise Exception(f"Failed to create carousel item container: {response}")
        
        child_container_ids.append(response["id"])
        print(f"Created carousel item container for {img_path.name}: {response['id']}")

    # Step 2: Create the main carousel container combining all slides
    carousel_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    caption = (
        "What was once impossible or required a dedicated team is now fully automated in 90 minutes. "
        "Here is the exact structural breakdown.\n\n"
        "Explore the full operational protocol at fmframeworks.gumroad.com\n\n"
        "#TheCompressionSystem #DigitalProducts #SystemArchitect #Automation"
    )
    
    carousel_payload = {
        "media_type": "CAROUSEL",
        "children": ",".join(child_container_ids),
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    
    carousel_response = requests.post(carousel_url, data=carousel_payload).json()
    if "id" not in carousel_response:
        raise Exception(f"Failed to create main carousel container: {carousel_response}")
    
    creation_id = carousel_response["id"]
    print(f"Main carousel container created: {creation_id}.")

    # Step 3: Poll Meta until the container finishes processing
    wait_for_container_ready(creation_id)

    # Step 4: Publish the container once ready
    print("Publishing container to feed...")
    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }
    
    publish_response = requests.post(publish_url, data=publish_payload).json()
    if "id" not in publish_response:
        raise Exception(f"Failed to publish carousel: {publish_response}")
        
    published_media_id = publish_response['id']
    print(f"Successfully published Instagram Carousel! Post ID: {published_media_id}")

    # Step 5: Drop generic automated comment from FM
    comment_url = f"https://graph.facebook.com/v19.0/{published_media_id}/comments"
    comment_payload = {
        "message": "FM — Full operational protocol & sovereign frameworks available at fmframeworks.gumroad.com",
        "access_token": ACCESS_TOKEN
    }
    
    comment_response = requests.post(comment_url, data=comment_payload).json()
    if "id" in comment_response:
        print(f"Successfully posted automated generic comment! Comment ID: {comment_response['id']}")
    else:
        print(f"Warning: Failed to post automatic comment: {comment_response}")

if __name__ == "__main__":
    publish_carousel_to_ig()
