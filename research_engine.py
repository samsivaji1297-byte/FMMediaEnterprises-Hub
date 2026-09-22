import os
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from google import genai

def run_research(topic="High Agency Mindset and Systemic Execution"):
    print(f"[INFO] Fetching real-time search signals for: '{topic}'...")

    try:
        results = list(DDGS().text(topic, max_results=5))
        if not results:
            print("[WARN] DuckDuckGo returned no results.")
            search_context = "No live search context available."
        else:
            search_context = "\n\n".join(
                [f"Source ({r.get('href', 'N/A')}):\nTitle: {r.get('title', '')}\nSnippet: {r.get('body', '')}" for r in results]
            )
            print("[INFO] Successfully retrieved SERP signals from DuckDuckGo.")
    except Exception as e:
        print(f"[ERROR] Failed to fetch DuckDuckGo results: {e}")
        search_context = "Search failed."

    prompt = f"""
    Analyze the following real-time search context on '{topic}' and compile a detailed research summary.

    SEARCH CONTEXT:
    {search_context}
    """

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    with open("research_summary.md", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("[SUCCESS] Research summary successfully saved to 'research_summary.md'.")

if __name__ == "__main__":
    import sys
    topic_arg = sys.argv[1] if len(sys.argv) > 1 else "High Agency Mindset and Systemic Execution"
    run_research(topic_arg)
