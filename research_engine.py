import os
import sys
import re
from datetime import datetime
from google import genai
from google.genai import types
from google.genai.errors import ClientError

# Configuration
MODEL_ID = "gemini-1.5-flash"
RESEARCH_DIR = "ResearchFactory"


def get_gemini_client() -> genai.Client:
    """Initializes the SDK client using GEMINI_API_KEY from environment."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[DEBUG ERROR] GEMINI_API_KEY environment variable is missing!")
        sys.exit(1)
    print("[DEBUG] Gemini client initialized successfully.")
    return genai.Client(api_key=api_key)


def generate_seo_brief(target_topic: str) -> str:
    """Generates an SEO brief with Search Grounding fallback handling."""
    client = get_gemini_client()
    
    prompt = f"""
You are an elite SEO strategist. Perform research on the topic: "{target_topic}".

Generate a structured SEO Brief in Markdown with the following headings:
# Executive SEO Brief: {target_topic}
## 1. Search Intent & Audience Analysis
## 2. Content Gaps & Opportunities
## 3. Recommended Keywords & Topics
## 4. Proposed Article Outline (H1, H2, H3)

Keep it tactical and actionable.
"""

    # --- Attempt 1: Search-Grounded Generation ---
    print(f"\n[DEBUG] Starting Search-Grounded Research for: '{target_topic}'...")
    grounded_config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.3
    )

    try:
        chat = client.chats.create(model=MODEL_ID, config=grounded_config)
        response = chat.send_message(prompt)
        
        brief_text = response.text.strip() if response and response.text else ""
        print("[DEBUG] Search-Grounded Research completed successfully!")

        # Log search queries used if available
        try:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                queries = getattr(candidate.grounding_metadata, 'web_search_queries', []) or []
                if queries:
                    print(f"[DEBUG] Search queries executed by Gemini: {queries}")
                    brief_text += "\n\n---\n### Search Queries Used:\n" + "\n".join([f"- `{q}`" for q in queries])
        except Exception as e:
            print(f"[DEBUG] Notice: Could not parse grounding metadata ({e})")

        return brief_text

    except ClientError as e:
        print(f"[DEBUG WARN] Grounded search hit an API limit: {e}")
        print("[DEBUG] Switching immediately to Fallback Mode (Standard Generation)...")
    except Exception as e:
        print(f"[DEBUG WARN] Grounded search failed with error: {e}")
        print("[DEBUG] Switching immediately to Fallback Mode (Standard Generation)...")

    # --- Attempt 2: Fallback (Standard Generation without tools) ---
    print("\n[DEBUG] Running Standard Gemini Generation (No Search Tools)...")
    standard_config = types.GenerateContentConfig(temperature=0.3)
    
    try:
        chat = client.chats.create(model=MODEL_ID, config=standard_config)
        response = chat.send_message(prompt)
        brief_text = response.text.strip() + "\n\n---\n*Note: Generated via Gemini parametric model due to search quota limits.*"
        print("[DEBUG] Standard generation completed successfully!")
        return brief_text
    except Exception as e:
        print(f"[DEBUG ERROR] Standard generation failed: {e}")
        sys.exit(1)


def save_brief(topic: str, content: str) -> str:
    """Saves the generated content to a Markdown file in ResearchFactory."""
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    
    clean_topic = re.sub(r'[^\w\-_]', '_', topic.replace(" ", "_"))
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"SEO_Brief_{clean_topic}_{timestamp}.md"
    filepath = os.path.join(RESEARCH_DIR, filename)

    print(f"\n[DEBUG] Writing SEO Brief to file: {filepath}")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print("[DEBUG] File saved successfully!")
    return filepath


if __name__ == "__main__":
    target_topic = sys.argv[1] if len(sys.argv) > 1 else "High Agency Mindset and Systemic Execution"
    print(f"=== Research Engine Triggered for Topic: '{target_topic}' ===")
    
    brief = generate_seo_brief(target_topic)
    save_brief(target_topic, brief)
    
    print("=== Research Engine Completed Successfully ===")
