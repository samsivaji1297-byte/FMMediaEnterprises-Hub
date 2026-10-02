import os
import re
import sys
import time
import random
from datetime import datetime, timezone
from pathlib import Path
from google import genai
from google.genai.errors import APIError

# --- Path Configurations ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR

RESEARCH_PRIMARY_PATH = PROJECT_ROOT / "ResearchFactory" / "latest_research.md"
RESEARCH_FALLBACK_PATH = PROJECT_ROOT / "latest_research.md"

DISTRIBUTION_DIR = PROJECT_ROOT / "DistributionPlatforms"

# --- Model Cascade Configuration ---
MODEL_CASCADE = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]

RECOGNITION_EVENT_PROMPT = """
You are an elite Content Architect specializing in "Recognition-Event" assets and friction-based human psychology.

You have been provided raw forum text scraped from high-context communities (Reddit/Hacker News).

Your Job:
1. Extract the core HUMAN FRICTION (the unspoken emotional/psychological bottleneck).
2. Identify the UNDERLYING MECHANISM (why this friction exists, e.g., Decision Fatigue, Fear of Effort-Income Disconnect).
3. Transform this insight into 3 distinct, high-converting assets separated by exact delimitations:

===THREADS_START===
[Insert 3-4 standalone punchy posts designed to be read sequentially on Threads/X. Include a 2-line Reel Hook & Caption at the top.]
===THREADS_END===

===SUBSTACK_START===
[Insert Substack Long-Form Essay (400-600 words) dissecting the psychological mechanism, titled with a high-agency curiosity hook.]
===SUBSTACK_END===

===BLOGGER_START===
[Insert Blogger/SEO Article optimized for search intent, entity coverage, and practical execution.]
===BLOGGER_END===

RAW FORUM DATA PAYLOAD:
{raw_data_payload}
"""

def extract_section(content: str, tag_name: str) -> str:
    """
    Extracts content between explicit delimiters using regex first, falling back to string splitting.
    """
    pattern = rf"===\s*{tag_name}_START\s*===\s*(.*?)\s*===\s*{tag_name}_END\s*==="
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # Fallback to direct string split logic
    start_delim = f"==={tag_name}_START==="
    end_delim = f"==={tag_name}_END==="
    
    if start_delim in content and end_delim in content:
        return content.split(start_delim)[1].split(end_delim)[0].strip()
        
    return content.strip()


def generate_content_with_fallback(client: genai.Client, prompt: str) -> str:
    """
    Executes model generation across the fallback cascade with retry logic and backoff.
    """
    last_exception = None

    for model in MODEL_CASCADE:
        for attempt in range(1, 4):
            try:
                print(f"[*] Calling model: {model} (Attempt {attempt})")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                if response.text:
                    return response.text
                else:
                    raise ValueError("Model returned an empty text payload.")
            except APIError as api_err:
                last_exception = api_err
                print(f"[!] API Error on {model} (Attempt {attempt}): {api_err.message}")
            except Exception as e:
                last_exception = e
                print(f"[!] Unexpected error on {model} (Attempt {attempt}): {str(e)}")

            # Exponential backoff with jitter
            sleep_time = (2 ** attempt) + random.uniform(0.1, 0.5)
            time.sleep(sleep_time)

        print(f"[!] Exhausted retries for {model}. Cascading to next model...")

    raise RuntimeError(f"All model fallbacks failed. Last error: {last_exception}")


def process_latest_research():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[!] Fatal Error: 'GEMINI_API_KEY' environment variable missing.")
        sys.exit(1)

    # 1. Resolve research payload path safely
    if RESEARCH_PRIMARY_PATH.exists():
        research_path = RESEARCH_PRIMARY_PATH
    elif RESEARCH_FALLBACK_PATH.exists():
        research_path = RESEARCH_FALLBACK_PATH
    else:
        print(f"[!] Fatal Error: 'latest_research.md' not found in '{RESEARCH_PRIMARY_PATH}' or '{RESEARCH_FALLBACK_PATH}'.")
        sys.exit(1)

    print(f"[*] Loading raw research payload from: {research_path}")
    raw_payload = research_path.read_text(encoding="utf-8")

    # 2. Initialize Gemini Client
    client = genai.Client(api_key=api_key)
    prompt = RECOGNITION_EVENT_PROMPT.format(raw_data_payload=raw_payload)

    # 3. Generate content with fallback cascade
    print("[*] Generating Recognition Event asset suite via Gemini SDK...")
    content = generate_content_with_fallback(client, prompt)

    # 4. Extract target sections
    threads_content = extract_section(content, "THREADS")
    substack_content = extract_section(content, "SUBSTACK")
    blogger_content = extract_section(content, "BLOGGER")

    # 5. Timestamp formatting (UTC ISO standard)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")

    targets = [
        (DISTRIBUTION_DIR / "Threads", f"{timestamp}_threads_draft.md", "latest_threads.md", threads_content),
        (DISTRIBUTION_DIR / "Substack", f"{timestamp}_substack_draft.md", "latest_substack.md", substack_content),
        (DISTRIBUTION_DIR / "Blogger", f"{timestamp}_blogger_draft.md", "latest_blogger.md", blogger_content),
    ]

    # 6. Save timestamped archive files and overwrite pointer files
    for folder_path, timestamped_filename, latest_filename, body in targets:
        folder_path.mkdir(parents=True, exist_ok=True)

        archive_file = folder_path / timestamped_filename
        archive_file.write_text(body, encoding="utf-8")
        print(f"[+] Archived asset: {archive_file.relative_to(PROJECT_ROOT)}")

        latest_file = folder_path / latest_filename
        latest_file.write_text(body, encoding="utf-8")
        print(f"[+] Updated pointer: {latest_file.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    process_latest_research()
