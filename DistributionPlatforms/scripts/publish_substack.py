import os
import json
import requests

SUBSTACK_SID = os.environ.get("SUBSTACK_SESSION_COOKIE")

# Resolves to repo_root/dist/latest_payload.json regardless of execution path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PAYLOAD_FILE = os.path.join(BASE_DIR, "dist", "latest_payload.json")

def post_substack_note():
    if not SUBSTACK_SID:
        raise ValueError("Missing SUBSTACK_SESSION_COOKIE secret in repo settings.")

    if not os.path.exists(PAYLOAD_FILE):
        print(f"No payload found at {PAYLOAD_FILE}. Skipping execution.")
        return

    with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    note_body = data.get("substack_note")
    if not note_body:
        print("No Substack Note body found in JSON payload.")
        return

    url = "https://substack.com/api/v1/comment/feed"
    
    cookies = {
        "substack.sid": SUBSTACK_SID
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://substack.com",
        "Referer": "https://substack.com/notes"
    }

    payload = {
        "body": note_body,
        "tab": "subscribed",
        "reply_count": 0,
        "restack_count": 0
    }

    print("Dispatching Note payload to Substack...")
    response = requests.post(url, headers=headers, cookies=cookies, json=payload)

    if response.status_code in [200, 201]:
        print("Substack Note published successfully.")
    else:
        print(f"Failed to post Note. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)

if __name__ == "__main__":
    post_substack_note()
