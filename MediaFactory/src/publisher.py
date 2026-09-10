import os
import time
import json
import requests

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
GRAPH_API_VERSION = "v21.0"

def publish_latest_vault_reel():
    vault_dir = os.path.join("..", "vault")
    if not os.path.exists(vault_dir):
        print("Vault directory does not exist. No reels to publish.")
        return

    queue_file = os.path.join(vault_dir, "queue.json")
    posted_runs = []
    
    if os.path.exists(queue_file):
        with open(queue_file, "r", encoding="utf-8") as f:
            posted_runs = json.load(f).get("posted", [])

    runs = [d for d in os.listdir(vault_dir) if os.path.isdir(os.path.join(vault_dir, d))]
    runs.sort()

    target_run = None
    for run in runs:
        if run not in posted_runs:
            target_run = run
            break

    if not target_run:
        print("No pending reels found in vault.")
        return

    run_path = os.path.join(vault_dir, target_run)
    video_file = next((f for f in os.listdir(run_path) if f.endswith(".mp4")), None)
    caption_file = next((f for f in os.listdir(run_path) if f.endswith(".txt")), None)

    if not video_file or not caption_file:
        print(f"Incomplete vault assets in folder {target_run}.")
        return

    video_path = os.path.join(run_path, video_file)
    with open(os.path.join(run_path, caption_file), "r", encoding="utf-8") as f:
        caption_text = f.read()

    print(f"=== Publishing Reel via Meta Graph API: {target_run} ===")

    # Step 1: Initialize Single-Step Media Container
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media"
    
    # Open local MP4 video file binary
    with open(video_path, "rb") as video_bytes:
        payload = {
            "media_type": "REELS",
            "caption": caption_text,
            "access_token": ACCESS_TOKEN
        }
        files = {
            "video_file": (video_file, video_bytes, "video/mp4")
        }

        print("Uploading video binary to Meta Graph API...")
        res = requests.post(url, data=payload, files=files, timeout=120)

    res_data = res.json()
    creation_id = res_data.get("id")

    if not creation_id:
        print(f"Failed to create reel container: {res_data}")
        return

    print(f"Media container created successfully! ID: {creation_id}")

    # Step 2: Poll Container Processing Status
    status_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{creation_id}?fields=status_code&access_token={ACCESS_TOKEN}"
    status = ""
    attempts = 0

    while status != "FINISHED" and attempts < 25:
        time.sleep(6)
        status_res = requests.get(status_url, timeout=15).json()
        status = status_res.get("status_code", "")
        print(f"Processing status [{attempts + 1}/25]: {status}")
        
        if status == "FINISHED":
            break
        elif status in ("ERROR", "EXPIRED"):
            print(f"Container processing failed on Meta with status: {status_res}")
            return
        attempts += 1

    if status != "FINISHED":
        print("Media processing timed out.")
        return

    # Step 3: Publish Container to Live Feed
    publish_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media_publish"
    publish_res = requests.post(
        publish_url, 
        data={"creation_id": creation_id, "access_token": ACCESS_TOKEN}, 
        timeout=15
    )
    
    print(f"Publish response: {publish_res.text}")

    # Step 4: Mark as Posted in Queue
    posted_runs.append(target_run)
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump({"posted": posted_runs}, f, indent=4)

    print(f"Successfully published reel '{target_run}' to Instagram!")

if __name__ == "__main__":
    publish_latest_vault_reel()
