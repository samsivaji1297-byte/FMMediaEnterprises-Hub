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
    """Queries AI models to generate a multi-slide carousel deck following the Desire + Mechanism framework."""
    prompt = """
    You are an elite direct-response copywriter crafting a multi-slide Instagram carousel deck (4 slides total).
    
    Product & Framework Context:
    Digital operational frameworks (fmframeworks.gumroad.com), including 'The Compression System' 
    (building sellable products in 90 minutes) and the '90-Minute Protocol'.
    
    THE GOVERNING COPYWRITING FORMULA:
    Slide 1 (Hook): Existing Human Desire + Recognizable Tool/Mechanism + Specific Achievable Outcome (Curiosity Loop)
    Slide 2 (The Breakdown): Reveal the core mechanism or 3-step breakdown.
    Slide 3 (The Execution): Show the actionable process/prompt or system architecture.
    Slide 4 (The Call to Action): Drive them to explore fmframeworks.gumroad.com for the complete protocol.
    
    Return ONLY a valid JSON object containing an array of 4 slides, with no extra markdown or fluff:
    {
      "slides": [
        {
          "mainText": "BUILD A PRODUCT<br>IN 90 MINUTES<br>USING CLAUDE",
          "subText": "HERE IS THE EXACT PROMPT MECHANISM"
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
    * {{
