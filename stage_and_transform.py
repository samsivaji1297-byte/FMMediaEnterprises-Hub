import os
import google.generativeai as genai

# Setup Gemini API configuration
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

RECOGNITION_EVENT_PROMPT = """
You are an elite Content Architect specializing in "Recognition-Event" assets and friction-based human psychology.

You have been provided raw forum text scraped from high-context communities (Reddit/Hacker News).

Your Job:
1. Extract the core HUMAN FRICTION (the unspoken emotional/psychological bottleneck).
2. Identify the UNDERLYING MECHANISM (why this friction exists, e.g., Decision Fatigue, Fear of Effort-Income Disconnect).
3. Transform this insight into 3 distinct, high-converting assets:

---

### OUTPUT FORMAT REQUIREMENTS:

## 1. Recognition Event Reel & Caption
- **Reel Hook (On-Screen Text / Voiceover):** 2 lines maximum. Must provoke an immediate "fuck... that's me" realization.
- **Caption:** Tight, punchy prose. Expose the problem without offering a bloated 10-step system. Focus on decision removal.

## 2. Substack Long-Form Essay
- **Title:** High-agency, curiosity-driven title.
- **Thesis Statement:** First sentence must state the counter-intuitive truth.
- **Body:** 400-600 words dissecting the psychological mechanism, contrasting traditional "low agency" traps with the "high agency" solution.

## 3. Threads / Social Micro-Thread
- 3-4 standalone punchy posts designed to be read sequentially. Focus on zero-fluff friction removal.

---

RAW FORUM DATA PAYLOAD:
{raw_data_payload}
"""

def process_latest_research():
    if not os.path.exists("latest_research.md"):
        print("[!] Error: 'latest_research.md' not found.")
        return

    with open("latest_research.md", "r", encoding="utf-8") as f:
        raw_payload = f.read()

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = RECOGNITION_EVENT_PROMPT.format(raw_data_payload=raw_payload)

    print("[*] Generating Recognition Event asset suite via Gemini...")
    response = model.generate_content(prompt)

    # Ensure output directory exists
    os.makedirs("DistributionPlatforms", exist_ok=True)
    
    # Save staged output
    output_path = os.path.join("DistributionPlatforms", "staged_content.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"[+] Recognition Event suite successfully generated at: '{output_path}'")

if __name__ == "__main__":
    process_latest_research()
