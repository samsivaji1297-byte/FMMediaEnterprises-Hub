import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from config import get_client, get_groq_client, call_with_fallback, DEFAULT_HYBRID_CASCADE

def generate_ai_hook() -> dict:
    """Uses your multi-provider cascade to generate structured carousel hook text."""
    prompt = """
    You are an expert Instagram content engineer creating high-converting carousel hooks.
    Generate a compelling, staccato carousel hook for a high-value digital system/framework product.
    
    Return ONLY valid JSON matching this exact structure, with no extra markdown blocks or formatting:
    {
      "mainText": "High-impact uppercase title (2 to 4 words max, e.g., BUILD A PRODUCT)",
      "subText": "Conversational opening lead-in (3 to 6 words max, e.g., in 90 minutes using)",
      "accentText": "The core conversion trigger target (2 to 4 words max, e.g., these 4 triggers)"
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
    """Ensures template.html exists, injects AI text, and renders 1080x1350 PNG via Playwright."""
    template_path = Path(__file__).parent / 'template.html'
    
    if not template_path.exists():
        print("template.html missing. Generating self-healing default template...")
        default_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>IG Carousel Hook Studio</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@800;900&display=swap');
    :root { --bg-color: #050505; --text-white: #FFFFFF; --accent-red: #FF3B30; --line-color: #262626; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background-color: var(--bg-color); width: 1080px; height: 1350px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 120px 96px; overflow: hidden; }
    .content-wrapper { width: 100%; display: flex; flex-direction: column; align-items: center; text-align: center; }
    .hook-main { font-family: 'Inter', sans-serif; font-weight: 900; font-size: 5.7rem; line-height: 1.05; text-transform: uppercase; color: #FFFFFF; letter-spacing: -0.03em; margin-bottom: 28px; }
    .hook-sub { font-family: 'Instrument Serif', serif; font-size: 4.2rem; font-weight: 400; color: #FFFFFF; line-height: 1.2; position: relative; }
    .accent-word { position: relative; display: inline-block; white-space: nowrap; }
    .accent-word::after { content: ''; position: absolute; bottom: -8px; left: -4px; right: -4px; height: 8px; background-color: var(--accent-red); border-radius: 50px; transform: rotate(-1deg); }
    .divider-line { width: 65%; height: 3px; background-color: var(--line-color); margin-top: 96px; }
    .slide-dots { position: absolute; bottom: 60px; display: flex; gap: 16px; }
    .dot { width: 12px; height: 12px; border-radius: 50%; background-color: #333; }
    .dot.active { background-color: #3B82F6; }
  </style>
</head>
<body>
  <div class="content-wrapper">
    <div class="hook-main">BUILD A PRODUCT</div>
    <div class="hook-sub">in 90 minutes using <span class="accent-word">these 4 triggers</span></div>
    <div class="divider-line"></div>
  </div>
  <div class="slide-dots"><div class="dot active"></div><div class="dot"></div><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
</body>
</html>"""
        template_path.write_text(default_template, encoding='utf-8')

    print("Launching headless Playwright browser engine...")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page(viewport={'width': 1080, 'height': 1350})
        
        file_url = f"file://{template_path.resolve()}"
        print(f"Loading template from: {file_url}")
        page.goto(file_url, wait_until='networkidle')
        
        page.evaluate(f"""() => {{
            const mainEl = document.querySelector('.hook-main');
            const subEl = document.querySelector('.hook-sub');
            
            if (mainEl) mainEl.textContent = {json.dumps(hook_data['mainText'])};
            if (subEl) {{
                subEl.innerHTML = `{hook_data['subText']} <span class="accent-word">{hook_data['accentText']}</span>`;
            }}
        }}""")
        
        page.evaluate("document.fonts.ready")
        
        output_path = Path(__file__).parent / 'output-slide-1.png'
        page.screenshot(path=str(output_path), type='png')
        browser.close()
        
        print(f"Carousel slide successfully rendered and saved to: {output_path}")

if __name__ == "__main__":
    print("Initializing Autonomous Carousel Engine...")
    hook_payload = generate_ai_hook()
    print("Generated Hook Payload:", hook_payload)
    render_slide(hook_payload)
