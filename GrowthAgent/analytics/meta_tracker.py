import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

DB_PATH = SCRIPT_DIR.parent / "data" / "performance_db.json"


def get_meta_credentials():
    return {
        "access_token": os.environ.get("IG_ACCESS_TOKEN") or os.environ.get("META_GRAPH_ACCESS_TOKEN"),
        "ig_user_id": os.environ.get("IG_USER_ID") or os.environ.get("INSTAGRAM_ACCOUNT_ID")
    }


def publish_reel_to_instagram(video_url: str, caption: str) -> str:
    """
    Publishes a Reel to Instagram via Meta Graph API.
    Step 1: Create media container.
    Step 2: Poll status until READY.
    Step 3: Publish container.
    """
    creds = get_meta_credentials()
    access_token = creds["access_token"]
    ig_user_id = creds["ig_user_id"]

    if not access_token or not ig_user_id:
        print("[!] Cannot publish: IG_ACCESS_TOKEN or IG_USER_ID missing from environment.")
        return None

    print(f"[*] Initializing Reel container upload for user: {ig_user_id}...")
    container_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    container_payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": access_token
    }

    try:
        # Step 1: Create Container
        res = requests.post(container_url, data=container_payload, timeout=30)
        res_data = res.json()
        container_id = res_data.get("id")

        if not container_id:
            print(f"[!] Container creation failed: {res_data}")
            return None

        print(f"[+] Reel Container created successfully ID: {container_id}")

        # Step 2: Poll Status
        status_url = f"https://graph.facebook.com/v19.0/{container_id}"
        status_params = {"fields": "status_code", "access_token": access_token}

        for attempt in range(12):  # Poll up to 60s
            time.sleep(5)
            status_res = requests.get(status_url, params=status_params, timeout=10).json()
            status_code = status_res.get("status_code")
            print(f"[*] Processing status: {status_code} (attempt {attempt+1}/12)")

            if status_code == "FINISHED":
                break
            elif status_code == "ERROR":
                print("[!] Meta video processing failed.")
                return None

        # Step 3: Publish
        publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
        publish_payload = {
            "creation_id": container_id,
            "access_token": access_token
        }

        pub_res = requests.post(publish_url, data=publish_payload, timeout=30).json()
        media_id = pub_res.get("id")

        if media_id:
            print(f"[+] Reel LIVE on Instagram! Media ID: {media_id}")
            return media_id
        else:
            print(f"[!] Publish step failed: {pub_res}")
            return None

    except Exception as e:
        print(f"[!] Exception during Instagram Reel publish: {e}")
        return None


def fetch_reel_metrics(media_id: str) -> dict:
    """Queries Meta Graph API for Reel performance insights."""
    creds = get_meta_credentials()
    if not creds["access_token"] or not creds["ig_user_id"]:
        print("[!] Meta API credentials missing. Returning default metrics structure.")
        return {"views": 0, "reach": 0, "saves": 0, "shares": 0, "comments": 0, "retention_score": 0.0}

    url = f"https://graph.facebook.com/v19.0/{media_id}/insights"
    params = {
        "metric": "plays,reach,saved,shares,comments",
        "access_token": creds["access_token"]
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        metrics = {}
        if "data" in data:
            for item in data["data"]:
                metrics[item["name"]] = item["values"][0]["value"]

        views = metrics.get("plays", 0)
        saves = metrics.get("saved", 0)
        shares = metrics.get("shares", 0)
        
        retention_score = round(((saves * 3) + (shares * 2) + metrics.get("comments", 0)) / max(views, 1) * 100, 2)

        return {
            "views": views,
            "reach": metrics.get("reach", 0),
            "saves": saves,
            "shares": shares,
            "comments": metrics.get("comments", 0),
            "retention_score": retention_score
        }
    except Exception as e:
        print(f"[!] Meta API query error ({e}). Returning default zeros.")
        return {"views": 0, "reach": 0, "saves": 0, "shares": 0, "comments": 0, "retention_score": 0.0}


def record_reel_performance(media_id: str, script_payload: dict, metrics: dict):
    """Saves published Reel performance to performance_db.json."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    db = []
    if DB_PATH.exists():
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception:
            db = []

    entry = {
        "media_id": media_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "product_key": script_payload.get("product_key"),
        "hook_text": script_payload.get("scenes", [{}])[0].get("text_overlay", ""),
        "full_script": script_payload,
        "metrics": metrics
    }

    db.append(entry)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)
        
    print(f"[+] Performance log updated for media_id: {media_id}")
