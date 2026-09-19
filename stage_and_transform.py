import os
import sys
import glob
import random
import re
from datetime import datetime
import google.generativeai as genai

# ==============================================================================
# 1. Setup & Config
# ==============================================================================
SOURCE_DIR = "WritingFactory/Mindset"
DEST_DIR = "DistributionPlatforms/Blogger"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable missing.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
os.makedirs(DEST_DIR, exist_ok=True)


# ==============================================================================
# 2. File Selection & Parsing
# ==============================================================================
def get_random_unprocessed_file():
    source_files = glob.glob(f"{SOURCE_DIR}/*.md") + glob.glob(f"{SOURCE_DIR}/**/*.md", recursive=True)
    if not source_files:
        print(f"No source files found in {SOURCE_DIR}")
        return None

    # Track already processed files to avoid duplicates
    existing_staged = set(os.listdir(DEST_DIR))
    
    # Shuffle and find a file that hasn't been transformed yet
    random.shuffle(source_files)
    for filepath in source_files:
        filename = os.path.basename(filepath)
        if not any(filename.replace(".md", "") in staged for staged in existing_staged):
            return filepath
            
    print("All files in source directory have already been staged to Blogger.")
    return None

def extract_title_and_clean_body(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Match first H1 header (# Title)
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        title = h1_match.group(1).strip()
    else:
        # Fallback to filename without extension and clean up underscores
        title = os.path.basename(filepath).replace(".md", "").replace("_", " ")

    return title, content


# ==============================================================================
# 3. Gemini Transformation & Staging
# ==============================================================================
def transform_and_stage(filepath):
    title, raw_markdown = extract_title_and_clean_body(filepath)
    print(f"Selected source file: {filepath}")
    print(f"Extracted Title: {title}")

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
You are an expert content editor converting raw Markdown into publication-ready Blogger HTML.

Target Title: {title}

Instructions:
1. Convert the provided Markdown into clean, responsive HTML suitable for Blogger posts.
2. Structure headers with <h2> and <h3>, and use <p>, <ul>, <ol>, <li>, and <blockquote> correctly.
3. DO NOT output standard Markdown code blocks or wrapping ```html fences. Return ONLY the raw HTML body.

Raw Markdown:
{raw_markdown}
"""

    response = model.generate_content(prompt)
    html_body = response.text.strip()

    # Strip code block fences if generated
    if html_body.startswith("```html"):
        html_body = html_body[7:]
    if html_body.startswith("```"):
        html_body = html_body[3:]
    if html_body.endswith("```"):
        html_body = html_body[:-3]

    # Create YAML Frontmatter + HTML payload
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    staged_filename = f"Blogger_Mindset_{timestamp}.md"
    staged_filepath = os.path.join(DEST_DIR, staged_filename)

    staged_content = f"""---
title: "{title}"
tags: ["Mindset", "FM Media"]
status: "publish"
source_file: "{os.path.basename(filepath)}"
---

{html_body.strip()}
"""

    with open(staged_filepath, "w", encoding="utf-8") as f:
        f.write(staged_content)

    print(f"Successfully transformed and staged to: {staged_filepath}")
    return staged_filepath


if __name__ == "__main__":
    selected_file = get_random_unprocessed_file()
    if selected_file:
        transform_and_stage(selected_file)
