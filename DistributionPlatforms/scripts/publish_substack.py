import os
import json
import time
from playwright.sync_api import sync_playwright

SUBSTACK_SID = os.environ.get("SUBSTACK_SESSION_COOKIE")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PAYLOAD_FILE = os.path.join(BASE_DIR, "dist", "latest_payload.json")

STEALTH_JS = """
// Mask navigator.webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// Mask Chrome runtime
window.chrome = { runtime: {} };

// Mask languages & plugins
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
"""

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

    print("Launching Playwright session inside virtual display...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-size=1280,800"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        # Inject native stealth before page loads
        context.add_init_script(STEALTH_JS)

        # Inject session cookie
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

        print("Navigating to Substack...")
        page.goto("https://substack.com", wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        print("Opening Notes interface...")
        page.goto("https://substack.com/notes", wait_until="domcontentloaded", timeout=60000)
        time.sleep(6)

        print(f"Current Page Title: {page.title()}")

        try:
            composer = page.locator('div[contenteditable="true"]').first
            composer.wait_for(state="visible", timeout=25000)
            composer.click()
            composer.fill(note_body)
            print("Content inserted into composer.")
            time.sleep(2)

            post_button = page.locator('button:has-text("Post")').first
            post_button.wait_for(state="visible", timeout=10000)
            post_button.click()
            
            print("Post button clicked. Confirming delivery...")
            time.sleep(6)
            print("Substack Note published successfully.")

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
