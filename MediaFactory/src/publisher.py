import os
import time
import json
import requests
from pathlib import Path

# Resolve environment variables with broad secret aliases
IG_USER_ID = os.getenv("IG_USER_ID") or os.getenv("INSTAGRAM_ACCOUNT_ID")
ACCESS_TOKEN = (
    os.getenv("IG_ACCESS_TOKEN")
    or os.getenv("INSTAGRAM_ACCESS_TOKEN")
    or os.getenv("META_ACCESS_TOKEN")
)
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")  # E.g. 'owner/repo'
GRAPH_API_VERSION = "v21.0"

VAULT_DIR = Path(__file__).resolve().parent.parent / "vault"


def publish_latest_vault_reel():
    if not VAULT_DIR.exists():
        print("[!] Vault directory does not exist. No reels to publish.")
        return

    queue_file = VAULT_DIR / "queue.json"
    posted_runs = []

    if queue_file.exists():
        with open(queue_file, "r", encoding="utf-8") as f:
            posted_runs = json.load(f).get("posted", [])

    runs = [d.name for d in VAULT_DIR.iterdir() if d.is_dir()]
    runs.sort()  # Process oldest pending reel first

    target_run = next((r for r in runs if r not in posted_runs), None)

    if not target_run:
        print("[*] No pending reels found in vault.")
        return

    if not ACCESS_TOKEN or not IG_USER_ID:
        print("[!] Meta API credentials missing in environment variables.")
        return

    run_path = VAULT_DIR / target_run
    video_file = next((f.name for f in run_path.glob("*.mp4")), None)
    caption_file = next((f.name for f in run_path.glob("*.txt")), None)

    if not video_file or not caption_file:
        print(f"[!] Incomplete vault assets in folder {target_run}.")
        return

    with open(run_path / caption_file, "r", encoding="utf-8") as f:
        caption_text = f.read()

    raw_video_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/main/MediaFactory/vault/{target_run}/{video_file}"

    print(f"=== Publishing Reel via Meta Graph API: {target_run} ===")
    print(f"[*] Public Video URL: {raw_video_url}")

    # Step 1: Create Container
    create_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": raw_video_url,
        "caption": caption_text,
        "access_token": ACCESS_TOKEN,
    }

    res = requests.post(create_url, data=payload, timeout=30).json()
    creation_id = res.get("id")

    if not creation_id:
        print(f"[!] Failed to create container on Meta: {res}")
        return

    print(f"[+] Container created! ID: {creation_id}")

    # Step 2: Poll Container Status
    status_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{creation_id}?fields=status_code&access_token={ACCESS_TOKEN}"
    status = ""
    attempts = 0

    while status != "FINISHED" and attempts < 25:
        time.sleep(6)
        status_res = requests.get(status_url, timeout=15).json()
        status = status_res.get("status_code", "")
        print(f"[*] Processing status [{attempts + 1}/25]: {status}")

        if status == "FINISHED":
            break
        elif status in ("ERROR", "EXPIRED"):
            print(f"[!] Container processing failed on Meta: {status_res}")
            return
        attempts += 1

    if status != "FINISHED":
        print("[!] Media processing timed out on Meta servers.")
        return

    # Step 3: Publish Media
    publish_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media_publish"
    publish_res = requests.post(
        publish_url,
        data={"creation_id": creation_id, "access_token": ACCESS_TOKEN},
        timeout=15,
    )

    print(f"[+] Publish response: {publish_res.text}")

    posted_runs.append(target_run)
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump({"posted": posted_runs}, f, indent=4)

    print(f"[SUCCESS] Published reel '{target_run}' to Instagram!")


if __name__ == "__main__":
    publish_latest_vault_reel()
