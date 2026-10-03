import os
import sys
import json
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
        "access_token": os.environ.get("META_GRAPH_ACCESS_TOKEN"),
        "ig_user_id": os.environ.get("INSTAGRAM_ACCOUNT_ID")
    }


def fetch_reel_metrics(media_id: str) -> dict:
    """Queries Meta Graph API for Reel performance insights."""
    creds = get_meta_credentials()
    if not creds["access_token"] or not creds["ig_user_id"]:
        print("[!] Meta API credentials missing. Returning simulated test payload.")
        return {
            "views": 1250,
            "reach": 980,
            "saves": 84,
            "shares": 32,
            "comments": 19,
            "retention_score": 7.8
        }

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
        
        # Calculate retention score (Weighted by Saves & Shares)
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
        print(f"[!] Meta API query error ({e}). Returning fallback zeros.")
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


if __name__ == "__main__":
    print("[*] Testing Meta Tracker Module...")
    sample_metrics = fetch_reel_metrics("sample_media_123")
    print("Sample Metrics:", sample_metrics)
