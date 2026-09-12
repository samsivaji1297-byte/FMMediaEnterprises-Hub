import os
import json
import time
from playwright.sync_api import sync_playwright

SUBSTACK_SID = os.environ.get("SUBSTACK_SESSION_COOKIE")

# Resolve path to dist/latest_payload.json
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

    print("Launching Playwright browser session...")
    with sync_playwright() as p:
        # Launch Chromium browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        # Set session cookie
        context.add_cookies([{
            "name": "substack.sid",
            "value": SUBSTACK_SID,
            "domain": ".substack.com",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax"
        }])

        page = context.new_page()
        
        print("Navigating to Substack Notes page...")
        page.goto("https://substack.com/notes", wait_until="networkidle")
        time.sleep(3)

        # Check if Cloudflare challenge page is loaded
        if "Just a moment..." in page.title():
            print("Cloudflare challenge encountered. Waiting for verification...")
            time.sleep(5)

        # Locate the Note composition input box
        print("Locating Note composer...")
        composer_selector = 'div[contenteditable="true"]'
        
        try:
            page.wait_for_selector(composer_selector, timeout=15000)
            page.click(composer_selector)
            page.fill(composer_selector, note_body)
            print("Content inserted into composer.")
            time.sleep(1)

            # Click the submit/post button
            post_button_selector = 'button:has-text("Post"), button:has-text("Post note")'
            page.wait_for_selector(post_button_selector, timeout=5000)
            page.click(post_button_selector)
            
            print("Post button clicked. Waiting for confirmation...")
            time.sleep(5)
            print("Substack Note published successfully via browser automation.")

        except Exception as e:
            print(f"Error interacting with Substack UI: {e}")
            # Capture screenshot on failure for diagnostic purposes
            os.makedirs(os.path.join(BASE_DIR, "dist"), exist_ok=True)
            page.screenshot(path=os.path.join(BASE_DIR, "dist", "failure_screenshot.png"))
            print("Saved diagnostic screenshot to dist/failure_screenshot.png")
            browser.close()
            exit(1)

        browser.close()

if __name__ == "__main__":
    publish_note()
