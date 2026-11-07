import os
import requests
from pathlib import Path

# Meta Graph API Credentials from GitHub Secrets
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

def upload_image_to_hosting(image_path: Path) -> str:
    """
    Note: Meta's Graph API requires public image URLs for container creation. 
    If you publish via GitHub Actions, you can either host temporary images on an S3/ImgBB bucket, 
    or use your repository's raw GitHub CDN URL if committing the generated images back to the repo.
    """
    # Assuming images are pushed or hosted, or using a raw GitHub content URL pattern:
    repo_name = os.getenv("GITHUB_REPOSITORY", "FMMediaEnterprises/FMMediaEnterprises-Hub")
    branch = "main"
    relative_path = f"ContentFactory/carousel/{image_path.name}"
    raw_url = f"https://raw.githubusercontent.com/{repo_name}/{branch}/{relative_path}"
    print(f"Using public asset URL for Meta API: {raw_url}")
    return raw_url

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
    print(f"Main carousel container created: {creation_id}. Publishing to feed...")

    # Step 3: Publish the container
    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }
    
    publish_response = requests.post(publish_url, data=publish_payload).json()
    if "id" not in publish_response:
        raise Exception(f"Failed to publish carousel: {publish_response}")
        
    print(f"Successfully published Instagram Carousel! Post ID: {publish_response['id']}")

if __name__ == "__main__":
    publish_carousel_to_ig()
