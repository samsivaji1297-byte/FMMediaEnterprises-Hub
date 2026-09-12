import os
import json
import requests

SUBSTACK_SID = os.environ.get("SUBSTACK_SESSION_COOKIE")
PAYLOAD_FILE = "dist/latest_payload.json"

def post_substack_note():
    if not SUBSTACK_SID:
        raise ValueError("Missing SUBSTACK_SESSION_COOKIE secret.")

    if not os.path.exists(PAYLOAD_FILE):
        print(f"No payload found at {PAYLOAD_FILE}. Skipping.")
        return

    with open(PAYLOAD_FILE, "r") as f:
        data = json.load(f)

    note_body = data.get("substack_note")
    if not note_body:
        print("No Substack Note found in payload.")
        return

    # Endpoint and headers setup
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

    # Draft standard raw text payload
    payload = {
        "body": note_body,
        "tab": "subscribed",
        "reply_count": 0,
        "restack_count": 0
    }

    print("Dispatching Note to Substack...")
    response = requests.post(url, headers=headers, cookies=cookies, json=payload)

    if response.status_code in [200, 201]:
        print("Substack Note published successfully.")
        print(f"Response: {response.json()}")
    else:
        print(f"Failed to post Note. Status Code: {response.status_code}")
        print(f"Server Output: {response.text}")
        exit(1)

if __name__ == "__main__":
    post_substack_note()
