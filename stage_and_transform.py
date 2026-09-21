import os
import glob
import re
from google import genai
from google.genai import types

MODEL_ID = "gemini-3.6-flash"
RESEARCH_DIR = "ResearchFactory"
WRITING_DIR = "WritingFactory"

def get_latest_brief_path() -> str:
    """Finds the most recent research brief file in ResearchFactory."""
    files = glob.glob(os.path.join(RESEARCH_DIR, "*.md"))
    if not files:
        raise FileNotFoundError(f"No research briefs found in '{RESEARCH_DIR}'. Run research_engine.py first.")
    # Sort by modification time to get the latest file
    latest_file = max(files, key=os.path.getmtime)
    print(f"[DEBUG] Found latest research brief: {latest_file}")
    return latest_file

def extract_clean_title(brief_content: str, fallback_filename: str) -> str:
    """Extracts a clean post title from the brief H1 or Title Tag Options."""
    # Look for proposed title options in the brief first
    title_match = re.search(r'Option 1:\*\*?\s*(.+)', brief_content)
    if title_match:
        return title_match.group(1).strip()
    
    # Fallback: Look for the main H1 line
    h1_match = re.search(r'^#\s*(.+)', brief_content, re.MULTILINE)
    if h1_match:
        clean_h1 = h1_match.group(1).replace("Executive SEO Brief:", "").strip()
        return clean_h1

    # Fallback: Clean up raw filename (remove prefix and timestamp)
    base = os.path.basename(fallback_filename)
    clean_base = re.sub(r'^SEO_Brief_', '', base)
    clean_base = re.sub(r'_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.md$', '', clean_base)
    return clean_base.replace('_', ' ').title()

def transform_brief_to_article(brief_file_path: str):
    """Reads brief, generates full article, and saves clean Markdown output."""
    with open(brief_file_path, "r", encoding="utf-8") as f:
        brief_content = f.read()

    clean_title = extract_clean_title(brief_content, brief_file_path)
    print(f"[DEBUG] Extracted Clean Title: '{clean_title}'")

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = f"""
You are an expert content writer and industry authority. 

Using the following SEO Research Brief as your strict architectural guide, write a comprehensive, highly engaging, 1500+ word article.

---
RESEARCH BRIEF:
{brief_content}
---

INSTRUCTIONS:
1. Use the following exact Title as the primary H1 header at the top of the article:
   # {clean_title}
2. Follow all H2 and H3 subheadings outlined in the brief.
3. Write with depth, concrete examples, and zero generic AI jargon.
4. Format cleanly in Markdown with tables, lists, and bold emphasis where appropriate.
"""

    print("[DEBUG] Generating full article in WritingFactory...")
    chat = client.chats.create(model=MODEL_ID)
    response = chat.send_message(prompt)

    os.makedirs(WRITING_DIR, exist_ok=True)
    
    # Save formatted article using the clean title in the filename
    clean_filename_slug = re.sub(r'[^\w\-_]', '_', clean_title.replace(" ", "_"))
    output_path = os.path.join(WRITING_DIR, f"{clean_filename_slug}.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text.strip())

    print(f"[DEBUG] Full article saved to: {output_path}")
    return output_path, clean_title

if __name__ == "__main__":
    brief_path = get_latest_brief_path()
    article_path, post_title = transform_brief_to_article(brief_path)
    print(f"\n=== Transformation Complete ===")
    print(f"Article Ready: {article_path}")
    print(f"Clean Post Title: {post_title}")
