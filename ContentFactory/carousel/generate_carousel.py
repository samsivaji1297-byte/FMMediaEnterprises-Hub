import sys
from pathlib import Path

# Automatically inject the repository root into sys.path so config.py loads cleanly from the root directory
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import json
import os
import random
import time
from playwright.sync_api import sync_playwright
from config import get_client, get_groq_client, call_with_fallback, DEFAULT_HYBRID_CASCADE

# --- High-Status Dark Aesthetic Background Pool ---
BACKGROUND_POOL = [
    "https://images.unsplash.com/photo-1518458028785-8fbcd101ebb9?q=80&w=1080&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1513694203232-719a280e022f?q=80&w=1080&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1080&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?q=80&w=1080&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1080&auto=format&fit=crop"
]

def generate_carousel_deck() -> list:
    """Queries AI models to generate a multi-slide carousel deck focused on clarity, unlocked possibilities, and instructional authority."""
    prompt = """
    You are an elite direct-response copywriter crafting a multi-slide Instagram carousel deck (4 slides total).
    
    Product & Framework Context:
    Digital operational frameworks (fmframeworks.gumroad.com), including 'The Compression System', 
    'Operator Mindset Kit', and the '90-Minute Protocol'.
    
    CORE COPYWRITING MANDATE:
    - NEVER attack, lecture, or point out user failures. Do not use fear-based or pain-agitation hooks.
    - INSTEAD, focus on revelation, clarity, and structural leverage: Show what is now possible that wasn't possible before. Reveal hidden mechanics, operational blind spots, and how modern AI/automation pipelines compress weeks of work into minutes. People pay for absolute clarity and information architecture.
    
    THE 5 INSIGHTFUL & REVELATORY HOOK ARCHITECTURES:
    1. “Here’s how…” (Practical Clarity - e.g., HERE'S HOW TO COMPRESS A WEEK OF PRODUCT BUILDING INTO 90 MINUTES)
    2. “How to…” (New Capabilities - e.g., HOW TO DEPLOY AN AUTONOMOUS CONTENT PIPELINE WITHOUT CODE)
    3. “Here’s why…” (Information Gap / Mechanics - e.g., HERE'S WHY MANUAL CONTENT CREATION IS OBSOLETE)
    4. “The easiest way to…” (Frictionless Execution - e.g., THE EASIEST WAY TO TURN KNOWLEDGE INTO A SELLABLE ASSET)
    5. “Use this…” (Immediate Leverage - e.g., USE THIS PROMPT MECHANISM TO STRUCTURE YOUR ENTIRE OFFER)
    
    SLIDE STRUCTURE (4 slides total, strictly ordered 1 to 4):
    - Slide 1 (The Hook): Must use one of the 5 architectures above with tall uppercase stacking (<br>) focusing on unlocked potential or clarity.
    - Slide 2 (The Breakdown): Unpack the hidden mechanism or paradigm shift that makes this possible now.
    - Slide 3 (The Execution): Show the clean, actionable process or system architecture.
    - Slide 4 (The Call to Action): Guide them to fmframeworks.gumroad.com for the complete operational protocol.
    
    Return ONLY a valid JSON object containing an array of 4 slides, where each slide explicitly includes its sequence number (1 to 4), with no extra markdown or fluff:
    {
      "slides": [
        {
          "slideNumber": 1,
          "mainText": "HERE'S HOW TO BUILD<br>A DIGITAL PRODUCT<br>IN 90 MINUTES",
          "subText": "WHAT WAS ONCE IMPOSSIBLE IS NOW AUTOMATED"
        },
        {
          "slideNumber": 2,
          "mainText": "THE SHIFT:<br>FROM MANUAL GRIND<br>TO SYSTEMIC LEVERAGE",
          "subText": "HOW MODERN PIPELINES CHANGE THE EQUATION"
        },
        {
          "slideNumber": 3,
          "mainText": "STEP 1:<br>EXTRACT THE CORE<br>KNOWLEDGE ASSET",
          "subText": "ELIMINATE THE FRICTION & COMPRESS"
        },
        {
          "slideNumber": 4,
          "mainText": "GET THE FULL<br>COMPRESSION SYSTEM<br>PROTOCOL TODAY",
          "subText": "FMFRAMEWORKS.GUMROAD.COM"
        }
      ]
    }
    """

    def gemini_builder(model_name: str):
        def execute():
            client = get_client()
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text
        return execute

    def groq_builder(model_name: str):
        def execute():
            client = get_groq_client()
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        return execute

    raw_response = call_with_fallback(
        gemini_api_func_builder=gemini_builder,
        groq_api_func_builder=groq_builder,
        model_chain=DEFAULT_HYBRID_CASCADE
    )

    cleaned_text = raw_response.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
        
    data = json.loads(cleaned_text.strip())
    raw_slides = data.get("slides", [])
    
    # Enforce strict ascending numerical order (1 -> 2 -> 3 -> 4) to prevent reverse sequencing bugs
    sorted_slides = sorted(raw_slides, key=lambda x: int(x.get("slideNumber", 1)))
    return sorted_slides

def render_carousel(slides: list):
    """Renders each slide in the deck to a separate PNG using Playwright and fine-tuned editorial typography."""
    template_path = Path(__file__).parent / 'template.html'
    
    print(f"Launching headless Playwright browser engine for {len(slides)} slides...")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page(viewport={'width': 1080, 'height': 1350})
        
        for index, slide in enumerate(slides, start=1):
            raw_bg_url = random.choice(BACKGROUND_POOL)
            cache_buster = int(time.time()) + index
            selected_bg_url = f"{raw_bg_url}&cb={cache_buster}"
            
            print(f"Rendering Slide {index}/{len(slides)}...")
            
            embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Editorial IG Carousel Studio - Slide {index}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500;600&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      width: 1080px; height: 1350px; background: #000000;
      display: flex; flex-direction: column; justify-content: center; align-items: center;
      position: relative; overflow: hidden; font-family: 'Inter', sans-serif;
      -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
    }}
    .bg-image {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background-image: url('{selected_bg_url}');
      background-size: cover; background-position: center;
      filter: grayscale(100%) contrast(125%) brightness(45%); z-index: 1;
    }}
    .bg-overlay {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: radial-gradient(circle at center, rgba(10, 10, 10, 0.3) 0%, rgba(5, 5, 5, 0.9) 100%);
      z-index: 2;
    }}
    .content-wrapper {{
      position: relative; z-index: 3; width: 90%; max-width: 960px;
      display: flex; flex-direction: column; align-items: center; text-align: center;
      padding: 0 40px;
    }}
    .watermark {{
      font-size: 1.1rem; letter-spacing: 0.32em; text-transform: uppercase;
      color: rgba(255, 255, 255, 0.55); margin-bottom: 56px; font-weight: 500;
    }}
    .hook-main {{
      font-family: 'Playfair Display', serif; font-weight: 700; 
      font-size: clamp(3.0rem, 4.6vw, 4.6rem);
      line-height: 1.08; text-transform: uppercase; color: #FFFFFF; letter-spacing: -0.01em;
      text-shadow: 0 4px 28px rgba(0, 0, 0, 0.9); margin-bottom: 44px;
      word-break: break-word; overflow-wrap: break-word;
    }}
    .hook-sub {{
      font-family: 'Inter', sans-serif; font-size: 1.15rem; font-weight: 500;
      letter-spacing: 0.25em; text-transform: uppercase; color: rgba(255, 255, 255, 0.85);
      text-shadow: 0 2px 12px rgba(0, 0, 0, 0.9);
      word-break: break-word; overflow-wrap: break-word; max-width: 100%;
    }}
  </style>
</head>
<body>
  <div class="bg-image"></div>
  <div class="bg-overlay"></div>
  <div class="content-wrapper">
    <div class="watermark">@FMMEDIAENTERPRISES • {index}/{len(slides)}</div>
    <div class="hook-main">{slide['mainText']}</div>
    <div class="hook-sub">{slide['subText']}</div>
  </div>
</body>
</html>"""
            
            template_path.write_text(embedded_template, encoding='utf-8')
            file_url = f"file://{template_path.resolve()}"
            page.goto(file_url, wait_until='networkidle')
            page.evaluate("document.fonts.ready")
            
            output_path = Path(__file__).parent / f'output-slide-{index}.png'
            page.screenshot(path=str(output_path), type='png')
            print(f"Saved {output_path.name}")
            
        browser.close()
    print("All carousel slides rendered successfully with locked sequence and fluid text scaling.")

if __name__ == "__main__":
    print("Initializing Multi-Slide Autonomous Carousel Engine...")
    slides_payload = generate_carousel_deck()
    print(f"Parsed and sequenced {len(slides_payload)} slides from AI model.")
    render_carousel(slides_payload)
