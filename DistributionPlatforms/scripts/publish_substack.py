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
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9"
            }
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
        
        # Mask navigator.webdriver
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        print("Navigating to Substack Notes page...")
        page.goto("https://substack.com/notes", wait_until="domcontentloaded", timeout=60000)

        # Wait up to 20 seconds if Cloudflare challenge is present
        for i in range(4):
            if "Just a moment..." in page.title():
                print(f"Cloudflare challenge active, waiting... ({i+1}/4)")
                time.sleep(5)
            else:
                break

        print(f"Current Page Title: {page.title()}")
        print("Locating Note composer...")
        
        try:
            # Use Playwright's multi-locator fallback syntax instead of invalid CSS
            composer = (
                page.locator('div[contenteditable="true"]')
                .or_(page.locator('textarea'))
                .or_(page.get_by_placeholder("Pondering"))
            ).first

            composer.wait_for(state="visible", timeout=20000)
            composer.click()
            composer.fill(note_body)
            print("Content inserted into composer.")
            time.sleep(2)

            # Locate post button
            post_button = (
                page.locator('button:has-text("Post")')
                .or_(page.locator('button:has-text("Publish")'))
            ).first

            post_button.wait_for(state="visible", timeout=10000)
            post_button.click()
            
            print("Post button clicked. Waiting for request completion...")
            time.sleep(5)
            print("Substack Note published successfully via browser automation.")

        except Exception as e:
            print(f"Error interacting with Substack UI: {e}")
            os.makedirs(os.path.join(BASE_DIR, "dist"), exist_ok=True)
            screenshot_path = os.path.join(BASE_DIR, "dist", "failure_screenshot.png")
            page.screenshot(path=screenshot_path)
            print(f"Diagnostic screenshot saved to {screenshot_path}")
            browser.close()
            exit(1)

        browser.close()

if __name__ == "__main__":
    publish_note()
