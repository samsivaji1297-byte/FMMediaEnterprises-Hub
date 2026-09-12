import os
import json
from curl_cffi import requests

SUBSTACK_SID = os.environ.get("SUBSTACK_SESSION_COOKIE")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PAYLOAD_FILE = os.path.join(BASE_DIR, "dist", "latest_payload.json")

def publish_note():
    if not SUBSTACK_SID:
        raise ValueError("Missing SUBSTACK_SESSION_COOKIE environment variable.")

    if not os.path.exists(PAYLOAD_FILE):
        print(f"No payload file found at {PAYLOAD_FILE}. Skipping execution.")
        return

    with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    note_body = data.get("substack_note")
    if not note_body:
        print("No Substack Note content found in JSON payload.")
        return

    print("Constructing Substack API request with TLS Impersonation...")

    url = "https://substack.com/api/v1/comment"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://substack.com",
        "Referer": "https://substack.com/notes"
    }

    cookies = {
        "substack.sid": SUBSTACK_SID
    }

    payload = {
        "body": note_body,
        "tab": "notes",
        "type": "note"
    }

    # Impersonate browser TLS fingerprint (chrome120)
    response = requests.post(
        url, 
        headers=headers, 
        cookies=cookies, 
        json=payload, 
        impersonate="chrome120",
        timeout=30
    )

    if response.status_code in (200, 201):
        print("Substack Note published successfully via API.")
        print(f"Response: {response.text}")
    else:
        print(f"Failed to post Note. HTTP Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        exit(1)

if __name__ == "__main__":
    publish_note()
