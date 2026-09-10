import os
import time
import json
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
GRAPH_API_VERSION = "v21.0"

def publish_latest_vault_reel():
    vault_dir = os.path.join("..", "vault")
    if not os.path.exists(vault_dir):
        print("Vault directory does not exist. No reels to publish.")
        return

    # Find unposted runs by checking queue history or scanning vault folders
    queue_file = os.path.join(vault_dir, "queue.json")
    posted_runs = []
    
    if os.path.exists(queue_file):
        with open(queue_file, "r", encoding="utf-8") as f:
            posted_runs = json.load(f).get("posted", [])

    runs = [d for d in os.listdir(vault_dir) if os.path.isdir(os.path.join(vault_dir, d))]
    runs.sort()  # Process oldest pending reel first

    target_run = None
    for run in runs:
        if run not in posted_runs:
            target_run = run
            break

    if not target_run:
        print("No pending reels found in vault.")
        return

    run_path = os.path.join(vault_dir, target_run)
    
    # Locate video and caption files
    video_file = next((f for f in os.listdir(run_path) if f.endswith(".mp4")), None)
    caption_file = next((f for f in os.listdir(run_path) if f.endswith(".txt")), None)

    if not video_file or not caption_file:
        print(f"Incomplete vault assets in folder {target_run}.")
        return

    video_path = os.path.join(run_path, video_file)
    with open(os.path.join(run_path, caption_file), "r", encoding="utf-8") as f:
        caption_text = f.read()

    print(f"=== Publishing Reel: {target_run} ===")

    # Step 1: Initialize Resumable Video Upload Session
    create_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "caption": caption_text,
        "access_token": ACCESS_TOKEN,
        "upload_type": "resumable"
    }

    res = requests.post(create_url, data=payload, timeout=15)
    res_data = res.json()
    creation_id = res_data.get("id")
    uri = res_data.get("uri")

    if not creation_id or not uri:
        print(f"Failed to create media container: {res_data}")
        return

    # Step 2: Upload Video Bytes Directly
    print(f"Uploading video file to Meta servers...")
    with open(video_path, "rb") as vf:
        file_bytes = vf.read()

    upload_headers = {
        "Authorization": f"OAuth {ACCESS_TOKEN}",
        "file_offset": "0"
    }
    upload_res = requests.post(uri, headers=upload_headers, data=file_bytes, timeout=120)
    
    if upload_res.status_code not in (200, 201):
        print(f"Video upload failed: {upload_res.text}")
        return

    # Step 3: Poll Container Processing Status
    status_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{creation_id}?fields=status_code&access_token={ACCESS_TOKEN}"
    status = ""
    attempts = 0

    while status != "FINISHED" and attempts < 20:
        time.sleep(5)
        status_res = requests.get(status_url, timeout=15).json()
        status = status_res.get("status_code", "")
        print(f"Processing status [{attempts + 1}/20]: {status}")
        
        if status == "FINISHED":
            break
        elif status in ("ERROR", "EXPIRED"):
            print(f"Container failed with status: {status}")
            return
        attempts += 1

    if status != "FINISHED":
        print("Media processing timed out.")
        return

    # Step 4: Publish Reel
    publish_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media_publish"
    publish_res = requests.post(publish_url, data={"creation_id": creation_id, "access_token": ACCESS_TOKEN}, timeout=15)
    
    print(f"Publish response: {publish_res.text}")

    # Step 5: Mark as Posted in Queue Tracker
    posted_runs.append(target_run)
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump({"posted": posted_runs}, f, indent=4)

    print(f"Successfully posted reel '{target_run}' and updated queue!")

if __name__ == "__main__":
    publish_latest_vault_reel()
