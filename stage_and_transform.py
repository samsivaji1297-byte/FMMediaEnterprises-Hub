import os
import re
from google import genai
from google.genai.errors import APIError

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

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
    if not os.path.exists("latest_research.md"):
        print("[!] Error: 'latest_research.md' not found.")
        return

    with open("latest_research.md", "r", encoding="utf-8") as f:
        raw_payload = f.read()

    model = genai.GenerativeModel("gemini-3.6-flash")
    prompt = RECOGNITION_EVENT_PROMPT.format(raw_data_payload=raw_payload)

    print("[*] Generating Recognition Event asset suite via Gemini...")
    response = model.generate_content(prompt)
    content = response.text

    # Extract sections using delimiters
    def extract_section(start_delim, end_delim):
        if start_delim in content and end_delim in content:
            return content.split(start_delim)[1].split(end_delim)[0].strip()
        return content

    threads_content = extract_section("===THREADS_START===", "===THREADS_END===")
    substack_content = extract_section("===SUBSTACK_START===", "===SUBSTACK_END===")
    blogger_content = extract_section("===BLOGGER_START===", "===BLOGGER_END===")

    # Output paths matching your exact folder architecture
    targets = [
        ("DistributionPlatforms/Threads", "threads_draft.md", threads_content),
        ("DistributionPlatforms/Substack", "substack_draft.md", substack_content),
        ("DistributionPlatforms/Blogger", "blogger_draft.md", blogger_content),
    ]

    for folder, filename, body in targets:
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"[+] Saved asset: {file_path}")

if __name__ == "__main__":
    process_latest_research()
