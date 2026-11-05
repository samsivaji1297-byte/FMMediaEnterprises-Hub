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

    # Execute through your standardized fallback cascade
    raw_response = call_with_fallback(
        gemini_api_func_builder=gemini_builder,
        groq_api_func_builder=groq_builder,
        model_chain=DEFAULT_HYBRID_CASCADE
    )

    # Clean and parse JSON response
    cleaned_text = raw_response.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
        
    return json.loads(cleaned_text.strip())

def render_slide(hook_data: dict):
    """Loads template.html, injects AI text, and renders 1080x1350 PNG via Playwright."""
    print("Launching headless Playwright browser engine...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page(viewport={'width': 1080, 'height': 1350})
        
        template_path = Path(__file__).parent / 'template.html'
        file_url = f"file://{template_path.resolve()}"
        
        print(f"Loading template from: {file_url}")
        page.goto(file_url, wait_until='networkidle')
        
        # Inject AI text payload into the DOM
        page.evaluate(f"""() => {{
            const mainEl = document.querySelector('.hook-main');
            const subEl = document.querySelector('.hook-sub');
            
            if (mainEl) mainEl.textContent = {json.dumps(hook_data['mainText'])};
            if (subEl) {{
                subEl.innerHTML = `{hook_data['subText']} <span class="accent-word">{hook_data['accentText']}</span>`;
            }}
        }}""")
        
        # Ensure remote fonts are fully loaded
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
