import json
import os
import random
import time
from pathlib import Path
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
    """Queries AI models to generate a multi-slide carousel deck using the 5 Instructional Hook Architectures."""
    prompt = """
    You are an elite direct-response copywriter crafting a multi-slide Instagram carousel deck (4 slides total).
    
    Product & Framework Context:
    Digital operational frameworks (fmframeworks.gumroad.com), including 'The Compression System', 
    'Operator Mindset Kit', and the '90-Minute Protocol'.
    
    THE 5 INSTRUCTIONAL HOOK ARCHITECTURES (Rotate or select one per generation):
    1. “Here’s how…” (Practical Authority - e.g., HERE'S HOW TO BUILD A DIGITAL PRODUCT THIS WEEKEND)
    2. “How to…” (Outcome Orientation - e.g., HOW TO TURN ONE IDEA INTO AN INCOME STREAM)
    3. “Here’s why…” (Information Gap - e.g., HERE'S WHY YOUR KNOWLEDGE IS WORTH MORE THAN YOU THINK)
    4. “The easiest way to…” (Reduced Friction - e.g., THE EASIEST WAY TO AUTOMATE REPETITIVE TASKS)
    5. “Use this…” (Immediate Utility - e.g., USE THIS PROMPT TO PACKAGE WHAT YOU KNOW)
    
    SLIDE STRUCTURE (4 slides total):
    - Slide 1 (The Hook): Must use one of the 5 instructional architectures above with tall uppercase stacking (<br>).
    - Slide 2 (The Breakdown): Reveal the core mechanism, workflow, or 3-step system.
    - Slide 3 (The Execution): Show the actionable process, prompt, or architectural breakdown.
    - Slide 4 (The Call to Action): Drive them to explore fmframeworks.gumroad.com for the complete protocol.
    
    Return ONLY a valid JSON object containing an array of 4 slides, with no extra markdown or fluff:
    {
      "slides": [
        {
          "mainText": "HERE'S HOW TO BUILD<br>A DIGITAL PRODUCT<br>IN 90 MINUTES",
          "subText": "USE THIS EXACT CLAUDE PROMPT MECHANISM"
        },
        {
          "mainText": "STEP 1:<br>EXTRACT THE CORE<br>KNOWLEDGE ASSET",
          "subText": "ELIMINATE THE FLUFF & COMPRESS"
        },
        {
          "mainText": "STEP 2:<br>DEPLOY THE SYSTEM<br>VIA AUTOMATION",
          "subText": "BUILD ONCE, RUN RECURSIVELY"
        },
        {
          "mainText": "GET THE FULL<br>COMPRESSION SYSTEM<br>PROTOCOL TODAY",
          "subText": "LINK IN BIO / FMFRAMEWORKS.GUMROAD.COM"
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
    return data.get("slides", [])

def render_carousel(slides: list):
    """Renders each slide in the deck to a separate PNG using Playwright and randomized background textures."""
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
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;600&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      width: 1080px; height: 1350px; background: #000000;
      display: flex; flex-direction: column; justify-content: center; align-items: center;
      position: relative; overflow: hidden; font-family: 'Inter', sans-serif;
    }}
    .bg-image {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background-image: url('{selected_bg_url}');
      background-size: cover; background-position: center;
      filter: grayscale(100%) contrast(125%) brightness(45%); z-index: 1;
    }}
    .bg-overlay {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: radial-gradient(circle at center, rgba(10, 10, 10, 0.35) 0%, rgba(5, 5, 5, 0.88) 100%);
      z-index: 2;
    }}
    .content-wrapper {{
      position: relative; z-index: 3; width: 85%;
      display: flex; flex-direction: column; align-items: center; text-align: center;
    }}
    .watermark {{
      font-size: 1.15rem; letter-spacing: 0.28em; text-transform: uppercase;
      color: rgba(255, 255, 255, 0.65); margin-bottom: 64px; font-weight: 600;
    }}
    .hook-main {{
      font-family: 'Playfair Display', serif; font-weight: 700; font-size: 4.8rem;
      line-height: 1.05; text-transform: uppercase; color: #FFFFFF; letter-spacing: 0.02em;
      text-shadow: 0 4px 24px rgba(0, 0, 0, 0.85); margin-bottom: 40px;
    }}
    .hook-sub {{
      font-family: 'Inter', sans-serif; font-size: 1.25rem; font-weight: 600;
      letter-spacing: 0.35em; text-transform: uppercase; color: rgba(255, 255, 255, 0.9);
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.9);
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
    print("All carousel slides rendered successfully.")

if __name__ == "__main__":
    print("Initializing Multi-Slide Autonomous Carousel Engine...")
    slides_payload = generate_carousel_deck()
    print(f"Parsed {len(slides_payload)} slides from AI model.")
    render_carousel(slides_payload)
