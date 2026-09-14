import os
import json
from datetime import datetime

VAULT_DIR = "MemoryVault"
DASHBOARD_FEED = os.path.join(VAULT_DIR, "dashboard_feed.json")
RELEASED_CONTENT = os.path.join(VAULT_DIR, "released_content.json")
ECHO_SCHEDULE = os.path.join(VAULT_DIR, "echo_schedule.json")

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def archive_dispatch():
    dispatch_id = os.getenv("DISPATCH_ID")
    platform = os.getenv("PLATFORM", "Unknown")
    mutated_text = os.getenv("MUTATED_TEXT", "")
    distributed_at = os.getenv("DISTRIBUTED_AT") or datetime.utcnow().isoformat()

    if not dispatch_id:
        print("Error: DISPATCH_ID environment variable missing.")
        return

    # 1. Read feeds
    pending_items = load_json(DASHBOARD_FEED)
    released_items = load_json(RELEASED_CONTENT)
    echo_items = load_json(ECHO_SCHEDULE)

    # 2. Extract item from pending
    target_item = None
    remaining_pending = []
    
    for item in pending_items:
        if str(item.get("id")) == str(dispatch_id):
            target_item = item
        else:
            remaining_pending.append(item)

    # If item wasn't found in pending, create a record from payload
    if not target_item:
        target_item = {
            "id": dispatch_id,
            "platform": platform,
            "content": mutated_text
        }

    # 3. Build released record
    released_record = {
        "id": target_item.get("id"),
        "platform": target_item.get("platform", platform),
        "content": target_item.get("content", mutated_text),
        "distributed_at": distributed_at,
        "status": "Released",
        "echo_stage": "Pending T+3"
    }

    released_items.insert(0, released_record)

    # 4. Save updated states
    save_json(DASHBOARD_FEED, remaining_pending)
    save_json(RELEASED_CONTENT, released_items)

    print(f"Successfully archived dispatch [{dispatch_id}] deployed at {distributed_at}")

if __name__ == "__main__":
    archive_dispatch()
