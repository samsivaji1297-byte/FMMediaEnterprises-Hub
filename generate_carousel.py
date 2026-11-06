import json
import os
import random
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from config import get_client, get_groq_client, call_with_fallback, DEFAULT_HYBRID_CASCADE

# --- High-Status Dark Aesthetic Background Pool ---
BACKGROUND_POOL = [
    # Cash / Currency Texture (Grayscale Moody)
    "https://images.unsplash.com/photo-1518458028785-8fbcd101ebb9?q=80&w=1080&auto=format&fit=crop",
    # Dark Architecture / Geometric Shadows
    "https://images.unsplash.com/photo-1513694203232-719a280e022f?q=80&w=1080&auto=format&fit=crop",
    # Dark Concrete / Slate Grain
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1080&auto=format&fit=crop",
    # Minimalist Luxury Light Shadows
    "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?q=80&w=1080&auto=format&fit=crop",
    # Dark Streetscape / Night Moody City
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1080&auto=format&fit=crop"
]

def generate_ai_hook() -> dict:
    """Queries AI models using the Desire + Mechanism + Curiosity Gap framework."""
    prompt = """
    You are an elite direct-response copywriter crafting high-status, editorial Instagram carousel hooks.
    
    Product & Framework Context:
    Digital operational frameworks (fmframeworks.gumroad.com), including 'The Compression System' 
    (building sellable products in 90 minutes) and the '90-Minute Protocol'.
    
    THE GOVERNING COPYWRITING FORMULA:
    Hook = Existing Human Desire + Recognizable Tool/Mechanism + Specific Achievable Outcome (Curiosity Loop)
    
    Rules for output generation:
    1. Focus on real human desires: Save time, make money, build sellable assets, eliminate manual work.
    2. Use recognizable mechanisms: Claude, ChatGPT, 90-minute workflows, zero-code pipelines.
    3. Formatting Structure:
       - mainText: A 4 to 6 word uppercase title split with line breaks (<br>) to form a tall, stacked editorial header (e.g., TURN ONE IDEA<br>INTO A PRODUCT or GET 8 HOURS<br>OF WORK DONE<br>IN 90 MINS).
       - subText: A clean, single-line high-tension curiosity kicker (e.g., USE THIS CLAUDE PROMPT THIS WEEKEND, IT'S NOT WHAT YOU THINK, HERE IS THE 4-STEP MECHANISM).
    
    Return ONLY valid JSON matching this exact structure, with no extra markdown or fluff:
    {
      "mainText": "...",
      "subText": "..."
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
        
    return json.loads(cleaned_text.strip())

def render_slide(hook_data: dict):
    """Dynamically writes template.html with cache-busted background image & renders PNG via Playwright."""
    template_path = Path(__file__).parent / 'template.html'
    
    # Pick a random background and append a timestamp cache-buster parameter
    raw_bg_url = random.choice(BACKGROUND_POOL)
    cache_buster = int(time.time())
    selected_bg_url = f"{raw_bg_url}&cb={cache_buster}"
    
    print(f"Selected Background Texture URL: {selected_bg_url}")
    
    # Embedded high-status editorial HTML/CSS template
    embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Editorial IG Carousel Studio</title>
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
      font-family: 'Playfair Display', serif; font-weight: 700; font-size: 5.2rem;
      line-height: 1.05; text-transform: uppercase; color: #FFFFFF; letter-spacing: 0.02em;
      text-shadow: 0 4px 24px rgba(0, 0, 0, 0.85); margin-bottom: 40px;
    }}
    .hook-sub {{
      font-family: 'Inter', sans-serif; font-size: 1.35rem; font-weight: 600;
      letter-spacing: 0.35em; text-transform: uppercase; color: rgba(255, 255, 255, 0.9);
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.9);
    }}
  </style>
</head>
<body>
  <div class="bg-image"></div>
  <div class="bg-overlay"></div>
  <div class="content-wrapper">
    <div class="watermark">@FMMEDIAENTERPRISES</div>
    <div class="hook-main">BUILD A PRODUCT<br>IN 90 MINUTES<br>USING CLAUDE</div>
    <div class="hook-sub">HERE IS THE EXACT PROMPT MECHANISM</div>
  </div>
</body>
</html>"""
    
    # Auto-write out the template file dynamically before headless browser execution
    template_path.write_text(embedded_template, encoding='utf-8')

    print("Launching headless Playwright browser engine...")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page(viewport={'width': 1080, 'height': 1350})
        
        file_url = f"file://{template_path.resolve()}"
        print(f"Loading template from: {file_url}")
        page.goto(file_url, wait_until='networkidle')
        
        # Inject AI copywriting payload directly into DOM
        page.evaluate(f"""() => {{
            const mainEl = document.querySelector('.hook-main');
            const subEl = document.querySelector('.hook-sub');
            
            if (mainEl) mainEl.innerHTML = {json.dumps(hook_data['mainText'])};
            if (subEl) subEl.textContent = {json.dumps(hook_data['subText'])};
        }}""")
        
        page.evaluate("document.fonts.ready")
        
        output_path = Path(__file__).parent / 'output-slide-1.png'
        page.screenshot(path=str(output_path), type='png')
        browser.close()
        
        print(f"High-Impact Editorial slide successfully rendered and saved to: {output_path}")

if __name__ == "__main__":
    print("Initializing Autonomous High-Status Carousel Engine...")
    hook_payload = generate_ai_hook()
    print("Generated Hook Payload:", hook_payload)
    render_slide(hook_payload)
