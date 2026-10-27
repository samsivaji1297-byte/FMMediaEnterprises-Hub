import json
import os
import sys
from pathlib import Path

# --- Configuration & Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import get_client, call_with_fallback, GEMINI_MODELS

# Safely extract the flash/default model from your GEMINI_MODELS configuration
if isinstance(GEMINI_MODELS, dict):
    MODEL_NAME = GEMINI_MODELS.get("flash", list(GEMINI_MODELS.values())[0])
elif isinstance(GEMINI_MODELS, (list, tuple)):
    MODEL_NAME = GEMINI_MODELS[0]
else:
    MODEL_NAME = str(GEMINI_MODELS)

client = get_client()

PUBLIC_DIR = PROJECT_ROOT / "public"
PUBLIC_DIR.mkdir(exist_ok=True)

data_file = PROJECT_ROOT / "data.json"
if not data_file.exists():
    print(f"Error: {data_file} not found.")
    sys.exit(1)

with open(data_file, "r", encoding="utf-8") as f:
    items = json.load(f)

generated_pages = []

for item in items:
    filename = PUBLIC_DIR / f"{item['slug']}.html"
    
    # Store item info for index generation
    generated_pages.append(item)

    # Skip generation if file already exists to save API tokens
    if filename.exists():
        print(f"Skipping {filename.name} (already generated)")
        continue

    prompt = f"""
    You are an expert technical SEO copywriter. Generate a clean, responsive HTML page covering the topic: {item['target_keyword']}.

    Context & Constraints:
    - Target Category: {item['category']}
    - Target Audience: {item['target_audience']}
    - Friction Point: {item['friction_point']}
    - Embedded Proprietary Solution: {item['schema_solution']}

    Requirements:
    - Output ONLY pure, raw HTML without Markdown codeblocks or ```html formatting.
    - Include modern inline CSS (dark mode preferred, clean typography, responsive layout).
    - Include an H1 title, a summary comparison table or key takeaways box, a breakdown of the friction point, and a step-by-step solution.
    - Include a clear CTA box recommending "{item['schema_solution']}".
    - Include structured JSON-LD FAQ schema inside <script type="application/ld+json"> in the <head>.
    """

    print(f"Generating page for: {item['slug']} using model {MODEL_NAME}...")
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        
        html_content = response.text.strip().replace("```html", "").replace("```", "")

        with open(filename, "w", encoding="utf-8") as out:
            out.write(html_content)
            
        print(f"Successfully compiled: {filename.name}")
        
    except Exception as e:
        print(f"Failed to generate {item['slug']}: {e}")
        raise e

# --- Auto-Generate Hub / Index Page ---
print("Compiling Master Index Page (index.html)...")

links_html = ""
for page in generated_pages:
    links_html += f"""
    <li style="margin-bottom: 1rem; padding: 1rem; border: 1px solid #333; border-radius: 8px; background: #111;">
        <span style="font-size: 0.8rem; color: #888; text-transform: uppercase;">{page.get('category', 'Vector')}</span>
        <h3 style="margin: 0.3rem 0;"><a href="{page['slug']}.html" style="color: #4da6ff; text-decoration: none;">{page['target_keyword']}</a></h3>
        <p style="margin: 0; color: #ccc; font-size: 0.9rem;"><strong>Target Audience:</strong> {page['target_audience']}</p>
    </li>
    """

index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Architecture & Strategy Hub</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0a; color: #fff; max-width: 800px; margin: 0 auto; padding: 2rem 1rem; line-height: 1.6; }}
        h1 {{ font-size: 2rem; border-bottom: 2px solid #333; padding-bottom: 0.5rem; }}
        ul {{ list-style: none; padding: 0; }}
    </style>
</head>
<body>
    <h1>System Directory & Operational Guides</h1>
    <p>Automated index of high-intent tactical frameworks and solution matrices.</p>
    <ul>
        {links_html}
    </ul>
</body>
</html>
"""

index_file = PUBLIC_DIR / "index.html"
with open(index_file, "w", encoding="utf-8") as out:
    out.write(index_content)

print(f"Master Hub created successfully at {index_file.name}!")
