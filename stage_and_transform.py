import os
import re
from datetime import datetime, timezone
from google import genai
from google.genai.errors import APIError

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

def process_latest_research():
    # 1. Read research payload from ResearchFactory
    research_path = os.path.join("ResearchFactory", "latest_research.md")
    if not os.path.exists(research_path):
        if os.path.exists("latest_research.md"):
            research_path = "latest_research.md"
        else:
            print("[!] Error: 'latest_research.md' not found in ResearchFactory/ or root.")
            return

    with open(research_path, "r", encoding="utf-8") as f:
        raw_payload = f.read()

    # 2. Initialize modern google-genai Client
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    prompt = RECOGNITION_EVENT_PROMPT.format(raw_data_payload=raw_payload)

    print("[*] Generating Recognition Event asset suite via Gemini...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    content = response.text

    # 3. Extract sections using delimiters
    def extract_section(start_delim, end_delim):
        if start_delim in content and end_delim in content:
            return content.split(start_delim)[1].split(end_delim)[0].strip()
        return content

    threads_content = extract_section("===THREADS_START===", "===THREADS_END===")
    substack_content = extract_section("===SUBSTACK_START===", "===SUBSTACK_END===")
    blogger_content = extract_section("===BLOGGER_START===", "===BLOGGER_END===")

    # 4. Generate timestamp string (matching ResearchFactory UTC naming)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")

    # Target folder definitions with platform-specific prefixes
    targets = [
        ("DistributionPlatforms/Threads", f"{timestamp}_threads_draft.md", "latest_threads.md", threads_content),
        ("DistributionPlatforms/Substack", f"{timestamp}_substack_draft.md", "latest_substack.md", substack_content),
        ("DistributionPlatforms/Blogger", f"{timestamp}_blogger_draft.md", "latest_blogger.md", blogger_content),
    ]

    # 5. Save timestamped archive files and overwrite latest pointers
    for folder, timestamped_file, latest_file, body in targets:
        os.makedirs(folder, exist_ok=True)
        
        # Save timestamped historical copy
        archive_path = os.path.join(folder, timestamped_file)
        with open(archive_path, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"[+] Archived asset: {archive_path}")

        # Overwrite latest pointer file
        latest_path = os.path.join(folder, latest_file)
        with open(latest_path, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"[+] Updated pointer: {latest_path}")

if __name__ == "__main__":
    process_latest_research()
