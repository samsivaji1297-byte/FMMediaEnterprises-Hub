import os
import sys
import time
import re
import yaml
import json
from datetime import datetime, timezone
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.genai import types

# --- Resolve Project Root & Path Configuration ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name != "scripts" else SCRIPT_DIR

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
        print("[!] Error: Missing required Blogger environment variables (BLOGGER_BLOG_ID, BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN).")
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
# 2. Markdown, Frontmatter & Schema Helpers
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


def strip_existing_json_ld(text: str) -> str:
    """Removes any pre-existing JSON-LD script blocks to prevent duplicate schema injection."""
    return re.sub(
        r'<script\s+type=["\']application/ld\+json["\']\s*>.*?</script>',
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    ).strip()


def extract_description_from_body(body: str, title: str) -> str:
    """Builds a clean description from Direct Answer or Executive Summary if present."""
    direct_match = re.search(r"\*\*Direct Answer:\*\*\s*(.+)", body)
    exec_match = re.search(r">?\s*\*\*Executive Summary:\*\*\s*(.+)", body)

    parts = []
    if direct_match:
        parts.append(re.sub(r"<[^>]+>", "", direct_match.group(1)).strip())
    if exec_match:
        parts.append(re.sub(r"<[^>]+>", "", exec_match.group(1)).strip())

    summary = " ".join(parts).strip()
    if summary:
        return summary[:300]
    return f"Operational diagnostic and execution architecture on {title}."[:300]


def clean_html_output(raw_html: str) -> str:
    """Strips markdown code fences and cleans raw HTML output."""
    raw_html = raw_html.strip()
    match = re.search(r"```(?:html)?\s*(.*?)\s*```", raw_html, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return raw_html


def inject_json_ld_schema(title: str, html_body: str, tags: list, description: str) -> str:
    """Injects a single BlogPosting + Organization JSON-LD block for search and AI crawlers."""
    cleaned_body = strip_existing_json_ld(html_body)
    published_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    clean_tags = [str(t).strip() for t in tags if str(t).strip()] if isinstance(tags, list) else []

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": "https://fmframeworks.gumroad.com/#organization",
                "name": "FM Media Enterprises",
                "url": "https://fmframeworks.gumroad.com/l/CompressionSystem",
            },
            {
                "@type": "BlogPosting",
                "headline": title[:110],
                "description": description[:300],
                "datePublished": published_iso,
                "dateModified": published_iso,
                "keywords": ", ".join(clean_tags),
                "author": {
                    "@type": "Organization",
                    "@id": "https://fmframeworks.gumroad.com/#organization",
                    "name": "FM Media Enterprises",
                },
                "publisher": {
                    "@type": "Organization",
                    "@id": "https://fmframeworks.gumroad.com/#organization",
                    "name": "FM Media Enterprises",
                },
                "mainEntityOfPage": {
                    "@type": "WebPage",
                },
            },
        ],
    }

    schema_script = f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'
    return schema_script + "\n" + cleaned_body


# ==============================================================================
# 3. Gemini Content Transformation (Model Cascade Integration)
# ==============================================================================
def transform_markdown_to_html(markdown_text: str, title: str) -> str:
    """
    Converts raw Markdown into clean HTML using the config.py model cascade.
    Includes a lightweight local fallback if all Gemini API endpoints fail.
    """
    clean_md = strip_existing_json_ld(markdown_text)

    prompt = f"""
You are an expert digital content editor converting Markdown into clean HTML for a Blogger post.

Target Title: {title}

Instructions:
1. Convert the provided Markdown body into modern, responsive, semantic HTML suitable for Blogger.
2. Maintain all original core points, links, tables, and voice, but polish readability, typography spacing, and inline layout where beneficial.
3. Wrap headers in standard HTML tags (<h2>, <h3>). Use <p>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <ul>, <ol>, <li>, <blockquote>, and <strong> tags appropriately.
4. DO NOT wrap the output in ```html ``` code fences or output any introductory/concluding conversational text. Output ONLY the raw HTML body.

Markdown Body:
{clean_md}
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
        html = clean_md
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
        latest_target = target_input / "latest_blogger.md"
        if latest_target.is_file():
            md_files = [latest_target]
        else:
            print(f"[*] Searching for Markdown files in: {target_input}")
            raw_files = list(target_input.glob("**/*.md")) if target_input.exists() else []
            md_files = [f for f in set(raw_files) if "latest_blogger.md" in f.name]

    if not md_files:
        print(f"[!] No Markdown files found for target: {target_input}.")
        return

    print(f"[*] Found {len(md_files)} file(s) to process.\n")
    service = get_blogger_service()

    for filepath in md_files:
        print(f"--- Processing: {filepath.relative_to(PROJECT_ROOT) if filepath.is_relative_to(PROJECT_ROOT) else filepath} ---")
        frontmatter, body = parse_markdown_file(filepath)

        title = frontmatter.get("title", "Sovereign Operator Briefing: Execution & Leverage Architecture")
        tags = frontmatter.get("tags", ["Productivity", "Systems", "Sovereign Operator", "Execution"])
        status = frontmatter.get("status", "publish")
        description = extract_description_from_body(body, title)

        print(f"Title: {title}")
        print(f"Status: {status}")
        print(f"Tags: {tags}")

        html_content = transform_markdown_to_html(body, title)

        if not html_content:
            print(f"[!] Skipping {filepath.name} due to transformation failure.\n")
            continue

        html_content = inject_json_ld_schema(title, html_content, tags, description)

        print("[*] Publishing to Blogger...")
        publish_post(service, title, html_content, tags, status)
        time.sleep(2)


if __name__ == "__main__":
    main()
