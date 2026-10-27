import json
import os
import sys
from pathlib import Path

# Resolve project root path for clean config imports
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Pull centralized config (client initialization & fallback logic)
from config import get_client, call_with_fallback, GEMINI_MODELS

# --- Configuration & Paths ---
client = get_client()

os.makedirs("public", exist_ok=True)

data_file = PROJECT_ROOT / "data.json"
if not data_file.exists():
    print(f"Error: {data_file} not found.")
    sys.exit(1)

with open(data_file, "r", encoding="utf-8") as f:
    items = json.load(f)

for item in items:
    filename = PROJECT_ROOT / "public" / f"{item['slug']}.html"
    
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

    print(f"Generating page for: {item['slug']} using model {GEMINI_MODELS}...")
    
    try:
        # Utilize your centralized call logic (or direct client call if preferred)
        response = client.models.generate_content(
            model=GEMINI_MODELS,
            contents=prompt
        )
        
        html_content = response.text.strip().replace("```html", "").replace("```", "")

        with open(filename, "w", encoding="utf-8") as out:
            out.write(html_content)
            
        print(f"Successfully compiled: {filename.name}")
        
    except Exception as e:
        print(f"Failed to generate {item['slug']}: {e}")

print("Build complete! All static pages generated in public/")
