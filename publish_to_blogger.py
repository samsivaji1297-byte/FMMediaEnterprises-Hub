import os
import sys
import glob
import time
import re
import yaml
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.genai import types

# --- Resolve Project Root & Path Configuration ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name != "publish_to_blogger.py" else SCRIPT_DIR

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import get_client, call_with_fallback

# ==============================================================================
# 1. Environment & Credentials Setup
# ==============================================================================
BLOG_ID = os.environ.get("BLOGGER_BLOG_ID")
CLIENT_ID = os.environ.get("BLOGGER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("BLOGGER_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("BLOGGER_REFRESH_TOKEN")

client = get_client()


def get_blogger_service():
    """
    Builds and returns an authorized Blogger API v3 service instance using OAuth refresh tokens.
    """
    if not all([BLOG_ID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        print("[!] Error: Missing required Blogger environment variables (BLOG_ID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN).")
        sys.exit(1)

    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/blogger"]
    )
    if not creds.valid:
        creds.refresh(Request())
    return build("blogger", "v3", credentials=creds)


# ==============================================================================
# 2. Markdown & Frontmatter Parsing
# ==============================================================================
def parse_markdown_file(filepath: Path):
    """
    Extracts YAML frontmatter and content body from a Markdown file.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
            except yaml.YAMLError as e:
                print(f"[!] Warning: Failed to parse YAML frontmatter in {filepath}: {e}")

    return frontmatter, body


def clean_html_output(raw_html: str) -> str:
    """Strips markdown code fences and cleans raw HTML output."""
    raw_html = raw_html.strip()
    match = re.search(r"```(?:html)?\s*(.*?)\s*```", raw_html, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return raw_html


# ==============================================================================
# 3. Gemini Content Transformation (Model Cascade Integration)
# ==============================================================================
def transform_markdown_to_html(markdown_text: str, title: str) -> str:
    """
    Converts raw Markdown into clean HTML using the config.py model cascade.
    Includes a lightweight local fallback if all Gemini API endpoints fail.
    """
    prompt = f"""
You are an expert digital content editor converting Markdown into clean HTML for a Blogger post.

Target Title: {title}

Instructions:
1. Convert the provided Markdown body into modern, responsive, semantic HTML suitable for Blogger.
2. Maintain all original core points and voice, but polish readability, typography spacing, and inline layout where beneficial.
3. Wrap headers in standard HTML tags (<h2>, <h3>). Use <p>, <ul>, <ol>, <li>, <blockquote>, and <strong> tags appropriately.
4. DO NOT wrap the output in ```html ``` code fences or output any introductory/concluding conversational text. Output ONLY the raw HTML body.

Markdown Body:
{markdown_text}
"""

    def _api_call_builder(target_model: str):
        def _api_call():
            print(f"[*] Transforming Markdown to HTML using model: {target_model}")
            
            gen_config = types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )
            
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=gen_config,
            )
            return response.text.strip()
        return _api_call

    try:
        raw_response = call_with_fallback(_api_call_builder)
        return clean_html_output(raw_response)
    except Exception as e:
        print(f"[!] Transformation cascade exhausted ({e}). Applying local markdown conversion fallback.")
        # Minimal local HTML fallback regex parsing
        html = markdown_text
        html = re.sub(r"^### (.*$)", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.*$)", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.*$)", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)
        paragraphs = html.split("\n\n")
        return "".join([f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()])


# ==============================================================================
# 4. Blogger API Distribution
# ==============================================================================
def publish_post(service, title: str, html_content: str, tags: list, status: str):
    """
    Posts the processed HTML to Google Blogger as a live post or a draft.
    """
    is_draft = True if str(status).lower() == "draft" else False

    body = {
        "kind": "blogger#post",
        "title": title,
        "content": html_content,
        "labels": tags if isinstance(tags, list) else []
    }

    try:
        request = service.posts().insert(
            blogId=BLOG_ID,
            body=body,
            isDraft=is_draft
        )
        response = request.execute()
        
        post_url = response.get("url", "Draft saved (no public URL yet)")
        status_label = "DRAFT" if is_draft else "PUBLISHED"
        print(f"[+] [{status_label}] Successfully created post: '{title}'")
        print(f"    URL: {post_url}\n")
        return response

    except Exception as e:
        print(f"[!] Error publishing post '{title}': {e}")
        return None


# ==============================================================================
# 5. Main Execution Flow
# ==============================================================================
def main():
    default_target = PROJECT_ROOT / "DistributionPlatforms" / "Blogger" / "latest_blogger.md"
    target_input = Path(sys.argv[1]) if len(sys.argv) > 1 else default_target

    if target_input.is_file():
        md_files = [target_input]
    else:
        print(f"[*] Searching for Markdown files in: {target_input}")
        raw_files = list(target_input.glob("**/*.md")) if target_input.exists() else []
        # Filter out timestamped archive files to avoid double posting historical runs
        md_files = [f for f in set(raw_files) if "latest_blogger.md" in f.name or not re.search(r"\d{4}-\d{2}-\d{2}", f.name)]

    if not md_files:
        print(f"[!] No Markdown files found for target: {target_input}.")
        return

    print(f"[*] Found {len(md_files)} file(s) to process.\n")
    service = get_blogger_service()

    for filepath in md_files:
        print(f"--- Processing: {filepath.relative_to(PROJECT_ROOT) if filepath.is_relative_to(PROJECT_ROOT) else filepath} ---")
        frontmatter, body = parse_markdown_file(filepath)

        title = frontmatter.get("title", "The Meta-Work Trap: Why Your Brain Chooses App Optimization Over Real Execution")
        tags = frontmatter.get("tags", ["Productivity", "Psychology", "Systems"])
        status = frontmatter.get("status", "publish")

        print(f"Title: {title}")
        print(f"Status: {status}")
        print(f"Tags: {tags}")

        html_content = transform_markdown_to_html(body, title)

        if not html_content:
            print(f"[!] Skipping {filepath.name} due to transformation failure.\n")
            continue

        print("[*] Publishing to Blogger...")
        publish_post(service, title, html_content, tags, status)
        time.sleep(2)


if __name__ == "__main__":
    main()
