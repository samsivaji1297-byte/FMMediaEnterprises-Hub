import os
import sys
import re
from datetime import datetime
from google import genai
from google.genai import types

# ==============================================================================
# 1. Environment & Setup
# ==============================================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
RESEARCH_DIR = "ResearchFactory"

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable missing.")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
os.makedirs(RESEARCH_DIR, exist_ok=True)


# ==============================================================================
# 2. SEO Research Function
# ==============================================================================
def run_seo_research(topic):
    print(f"--- Running Google Search Grounded Research on: '{topic}' ---")

    prompt = f"""
You are an elite SEO strategist and content researcher. Perform deep live web search research on the topic: "{topic}".

Conduct live Google searches to gather real-time SERP data and analyze current top-performing content.

Generate a comprehensive, structured SEO Brief in Markdown with the following sections:

# Executive SEO Brief: {topic}

## 1. Search Intent & Audience Analysis
- What are users actively looking for when searching this topic right now?
- Key pain points and questions currently being asked on forums and search results.

## 2. Live SERP Landscape & Content Gaps
- What are top-ranking articles focusing on?
- **Content Gaps:** What critical angles or insights are top-ranking pages MISSING that we can capitalize on?

## 3. High-Value Keywords & Semantic Concepts
- Core target keyword and primary LSI (Latent Semantic Indexing) keywords.
- Related search phrases and "People Also Ask" questions to answer in content.

## 4. Recommended Article Blueprint
- Proposed H1 Title options (optimized for CTR and search intent).
- Recommended H2 / H3 Outline for maximum depth and authority.
- Essential takeaways or counter-intuitive angles to include for maximum engagement.

Make the brief highly tactical, concise, and immediately actionable for an AI writing engine.
"""

    # Call Gemini 3.6 Flash with native Google Search Grounding enabled
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )

    brief_content = response.text.strip()

    # Extract grounding search queries used by Gemini if available
    search_queries = []
    try:
        candidate = response.candidates[0]
        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            search_queries = getattr(candidate.grounding_metadata, 'web_search_queries', [])
    except Exception:
        pass

    # Append source queries metadata at the bottom of the brief
    if search_queries:
        brief_content += "\n\n---\n### Grounded Search Queries Used:\n"
        for q in search_queries:
            brief_content += f"- `{q}`\n"

    # Save to ResearchFactory directory
    clean_topic = re.sub(r'[^\w\-_]', '_', topic.replace(" ", "_"))
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"SEO_Brief_{clean_topic}_{timestamp}.md"
    filepath = os.path.join(RESEARCH_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(brief_content)

    print(f"Successfully generated SEO Brief: {filepath}")
    return filepath


if __name__ == "__main__":
    # Target topic can be passed as a command-line argument, or fallback to default
    target_topic = sys.argv[1] if len(sys.argv) > 1 else "High Agency Mindset and Autonomous Systems 2026"
    run_seo_research(target_topic)
