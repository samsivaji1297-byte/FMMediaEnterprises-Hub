import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from config import get_client, get_groq_client, call_with_fallback, DEFAULT_HYBRID_CASCADE

def generate_ai_hook() -> dict:
    """Queries AI models for multi-line stacked editorial serif hooks."""
    prompt = """
    You are an elite direct-response copywriter crafting high-status, editorial Instagram hooks.
    Your goal is to create a compelling, curiosity-gap hook formatted as a stacked title.
    
    Context: Digital frameworks and sovereign operational systems (fmframeworks.gumroad.com), 
    such as 'The Compression System' (building products in 90 minutes) and the '90-Minute Protocol'.
    
    Formatting Rules:
    1. mainText: A 4-6 word uppercase title split with line breaks (<br>) to form a tall stack (e.g., THE REAL<br>SECRET<br>BEHIND<br>MAKING<br>MONEY or HOW TO<br>BUILD A<br>PRODUCT IN<br>90 MINS).
    2. subText: A short, high-tension uppercase subline/kicker (e.g., IT'S NOT WHAT YOU THINK, THE 4 HIDDEN TRIGGERS, UNLOCK THE PROTOCOL).
    
    Return ONLY valid JSON matching this exact structure:
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
    """Auto-generates template.html on the fly, injects editorial AI hook, and renders 1080x1350 PNG via Playwright."""
    template_path = Path(__file__).parent / 'template.html'
    
    # Embed the cinematic editorial template directly inside Python
    embedded_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Editorial IG Carousel Hook</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;600&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      width: 1080px; height: 1350px; background: #000000;
      display: flex; flex-direction: column; justify-content: center; align-items: center;
      position: relative; overflow: hidden; font-family: 'Inter', sans-serif;
    }
    .bg-image {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background-image: url('https://images.unsplash.com/photo-1518458028785-8fbcd101ebb9?q=80&w=1080&auto=format&fit=crop');
      background-size: cover; background-position: center;
      filter: grayscale(100%) contrast(120%) brightness(50%); z-index: 1;
    }
    .bg-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: radial-gradient(circle at center, rgba(10, 10, 10, 0.4) 0%, rgba(5, 5, 5, 0.85) 100%);
      z-index: 2;
    }
    .content-wrapper {
      position: relative; z-index: 3; width: 80%;
      display: flex; flex-direction: column; align-items: center; text-align: center;
    }
    .watermark {
      font-size: 1.1rem; letter-spacing: 0.25em; text-transform: uppercase;
      color: rgba(255, 255, 255, 0.6); margin-bottom: 60px; font-weight: 600;
    }
    .hook-main {
      font-family: 'Playfair Display', serif; font-weight: 700; font-size: 5.2rem;
      line-height: 1.05; text-transform: uppercase; color: #FFFFFF; letter-spacing: 0.02em;
      text-shadow: 0 4px 20px rgba(0, 0, 0, 0.8); margin-bottom: 36px;
    }
    .hook-sub {
      font-family: 'Inter', sans-serif; font-size: 1.3rem; font-weight: 600;
      letter-spacing: 0.35em; text-transform: uppercase; color: rgba(255, 255, 255, 0.85);
    }
  </style>
</head>
<body>
  <div class="bg-image"></div>
  <div class="bg-overlay"></div>
  <div class="content-wrapper">
    <div class="watermark">@FMMEDIAENTERPRISES</div>
    <div class="hook-main">THE REAL<br>SECRET<br>BEHIND<br>MAKING<br>MONEY</div>
    <div class="hook-sub">IT'S NOT WHAT YOU THINK</div>
  </div>
</body>
</html>"""
    
    # Write out the template dynamically before rendering
    template_path.write_text(embedded_template, encoding='utf-8')

    print("Launching headless Playwright browser engine...")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page(viewport={'width': 1080, 'height': 1350})
        
        file_url = f"file://{template_path.resolve()}"
        print(f"Loading template from: {file_url}")
        page.goto(file_url, wait_until='networkidle')
        
        # Inject dynamic stacked text payload into DOM
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
        
        print(f"Editorial slide successfully rendered and saved to: {output_path}")

if __name__ == "__main__":
    print("Initializing Single-File Editorial Carousel Engine...")
    hook_payload = generate_ai_hook()
    print("Generated Editorial Hook Payload:", hook_payload)
    render_slide(hook_payload)
