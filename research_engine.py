import os
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from google import genai

def run_research():
    # 1. Define target query / market demand topic
    topic = "Autonomous AI Workflows and Content Automation Tools"
    print(f"[INFO] Fetching real-time search signals for: '{topic}'...")

    # 2. Scrape live web context via DuckDuckGo (Zero API limits)
    try:
        results = DDGS().text(keywords=topic, max_results=5)
        if not results:
            print("[WARN] DuckDuckGo returned no results. Proceeding with fallback context.")
            search_context = "No live search context available."
        else:
            search_context = "\n\n".join(
                [f"Source ({r.get('href', 'N/A')}):\nTitle: {r.get('title', '')}\nSnippet: {r.get('body', '')}" for r in results]
            )
            print("[INFO] Successfully retrieved SERP signals from DuckDuckGo.")
    except Exception as e:
        print(f"[ERROR] Failed to fetch DuckDuckGo results: {e}")
        search_context = "Search failed. Rely on internal knowledge base."

    # 3. Construct prompt bypassing Google Search Grounding tools
    prompt = f"""
    You are an expert researcher for theFINALMindset and FMMediaEnterprises.
    Analyze the following real-time search context on '{topic}' and compile a detailed research summary.

    SEARCH CONTEXT:
    {search_context}

    Please cover:
    - Core problem & market demand overview
    - Key takeaways & high-impact solutions
    - Pain points / friction points users face
    - Potential content hooks or micro-angles
    """

    # 4. Generate summary via Gemini (Standard payload, no grounding tools attached)
    print("[INFO] Passing search context to Gemini for strategic synthesis...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # 5. Output research_summary.md for stage_and_transform.py
    output_filename = "research_summary.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"[SUCCESS] Research summary successfully saved to '{output_filename}'.")

if __name__ == "__main__":
    run_research()
