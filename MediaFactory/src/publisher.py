import os
import time
import json
import requests

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")  # E.g., 'username/repo'
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
    video_file = next((f for f in os.listdir(run_path) if f.endswith(".mp4")), None)
    caption_file = next((f for f in os.listdir(run_path) if f.endswith(".txt")), None)

    if not video_file or not caption_file:
        print(f"Incomplete vault assets in folder {target_run}.")
        return

    with open(os.path.join(run_path, caption_file), "r", encoding="utf-8") as f:
        caption_text = f.read()

    # Construct the direct raw public GitHub URL for Meta to ingest
    raw_video_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/main/MediaFactory/vault/{target_run}/{video_file}"

    print(f"=== Publishing Reel via Meta Graph API: {target_run} ===")
    print(f"Public Video URL: {raw_video_url}")

    # Step 1 — Create media container via public video URL (GAS pattern)
    create_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": raw_video_url,
        "caption": caption_text,
        "access_token": ACCESS_TOKEN
    }

    res = requests.post(create_url, data=payload, timeout=30)
    res_data = res.json()
    creation_id = res_data.get("id")

    if not creation_id:
        print(f"Failed to create reel container on Meta: {res_data}")
        return

    print(f"Media container created successfully! ID: {creation_id}")

    # Step 2 — Poll container processing status until FINISHED
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
            print(f"Container processing failed on Meta: {status_res}")
            return
        attempts += 1

    if status != "FINISHED":
        print("Media processing timed out on Meta servers.")
        return

    # Step 3 — Publish reel to live feed
    publish_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media_publish"
    publish_res = requests.post(
        publish_url, 
        data={"creation_id": creation_id, "access_token": ACCESS_TOKEN}, 
        timeout=15
    )
    
    print(f"Publish response: {publish_res.text}")

    # Step 4 — Mark run as posted in local queue
    posted_runs.append(target_run)
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump({"posted": posted_runs}, f, indent=4)

    print(f"Successfully published reel '{target_run}' to Instagram!")

if __name__ == "__main__":
    publish_latest_vault_reel()
