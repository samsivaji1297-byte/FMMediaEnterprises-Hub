import json
import os
import random
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from config import get_client, get_groq_client, call_with_fallback, DEFAULT_HYBRID_CASCADE

# --- Cinematic Video Background Loop Pool (Slow-Motion Moody B-Roll) ---
VIDEO_BG_POOL = [
    # Dark Architectural / Glass Motion Texture
    "https://assets.mixkit.co/videos/preview/mixkit-geometric-animation-of-futuristic-architecture-41584-large.mp4",
    # Moody Ambient Light Shadows
    "https://assets.mixkit.co/videos/preview/mixkit-dark-abstract-background-with-moving-lights-41961-large.mp4",
    # Abstract Luxury Dark Particles
    "https://assets.mixkit.co/videos/preview/mixkit-luxury-gold-and-black-background-animation-43098-large.mp4"
]

def generate_reel_hook() -> dict:
    """Queries AI models using the 5 Instructional Hook Architectures for high-retention video reels."""
    prompt = """
    You are an elite direct-response copywriter crafting a short, high-tension Instagram Reel hook.
    
    Product & Framework Context:
    Digital operational frameworks (fmframeworks.gumroad.com), including 'The Compression System', 
    'Operator Mindset Kit', and the '90-Minute Protocol'.
    
    THE 5 INSTRUCTIONAL HOOK ARCHITECTURES:
    1. “Here’s how…” (Practical Authority)
    2. “How to…” (Outcome Orientation)
    3. “Here’s why…” (Information Gap)
    4. “The easiest way to…” (Reduced Friction)
    5. “Use this…” (Immediate Utility)
    
    Rules for output generation:
    - mainText: A 4 to 6 word uppercase punchy title split with line breaks (<br>) optimized for centered reading on a vertical screen (e.g., HERE'S HOW TO BUILD<br>A PRODUCT IN 90 MINS).
    - subText: A clean, high-curiosity subline pointing to the system or prompt mechanism.
    
    Return ONLY valid JSON matching this exact structure, with no extra markdown or fluff:
    {
      "mainText": "...",
      "subText": "..."
    }
    """

    def gemini_builder(model_name: str):
        def execute():
            client = get_client()
            response = client.models.generate_content(model=model_name, contents=prompt)
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

def render_video_reel(hook_data: dict):
    """Renders a 1080x1920 cinematic video loop with centered typography using Playwright video recording."""
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    template_path = Path(__file__).parent / 'template.html'
    selected_video_url = random.choice(VIDEO_BG_POOL)
    print(f"Selected Cinematic Background Loop: {selected_video_url}")

    embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Editorial IG Reel Studio</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;600&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      width: 1080px; height: 1920px; background: #000000;
      display: flex; flex-direction: column; justify-content: center; align-items: center;
      position: relative; overflow: hidden; font-family: 'Inter', sans-serif;
    }}
    .bg-video {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      object-fit: cover; filter: grayscale(100%) contrast(130%) brightness(40%); z-index: 1;
    }}
    .bg-overlay {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: radial-gradient(circle at center, rgba(10, 10, 10, 0.4) 0%, rgba(0, 0, 0, 0.9) 100%);
      z-index: 2;
    }}
    .content-wrapper {{
      position: relative; z-index: 3; width: 85%;
      display: flex; flex-direction: column; align-items: center; text-align: center;
    }}
    .watermark {{
      font-size: 1.2rem; letter-spacing: 0.3em; text-transform: uppercase;
      color: rgba(255, 255, 255, 0.6); margin-bottom: 80px; font-weight: 600;
    }}
    .hook-main {{
      font-family: 'Playfair Display', serif; font-weight: 700; font-size: 5.4rem;
      line-height: 1.08; text-transform: uppercase; color: #FFFFFF; letter-spacing: 0.02em;
      text-shadow: 0 4px 30px rgba(0, 0, 0, 0.9); margin-bottom: 48px;
    }}
    .hook-sub {{
      font-family: 'Inter', sans-serif; font-size: 1.4rem; font-weight: 600;
      letter-spacing: 0.35em; text-transform: uppercase; color: rgba(255, 255, 255, 0.85);
      text-shadow: 0 2px 12px rgba(0, 0, 0, 0.9);
    }}
  </style>
</head>
<body>
  <video class="bg-video" autoplay muted loop playsinline>
    <source src="{selected_video_url}" type="video/mp4">
  </video>
  <div class="bg-overlay"></div>
  <div class="content-wrapper">
    <div class="watermark">@FMMEDIAENTERPRISES</div>
    <div class="hook-main">{hook_data['mainText']}</div>
    <div class="hook-sub">{hook_data['subText']}</div>
  </div>
</body>
</html>"""

    template_path.write_text(embedded_template, encoding='utf-8')

    print("Launching headless Playwright video recording engine...")
    with sync_playwright() as p:
        # Launch browser with video recording enabled at vertical 1080x1920 resolution
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox', '--autoplay-policy=no-user-gesture-required'])
        context = browser.new_context(
            viewport={'width': 1080, 'height': 1920},
            record_video_dir=str(output_dir),
            record_video_size={'width': 1080, 'height': 1920}
        )
        
        page = context.new_page()
        file_url = f"file://{template_path.resolve()}"
        page.goto(file_url, wait_until='networkidle')
        page.evaluate("document.fonts.ready")
        
        print("Recording 6-second cinematic reel loop...")
        time.sleep(6.0) # Duration of the recorded video loop
        
        context.close()
        browser.close()
        
        # Locate the recorded webm file and rename it cleanly to output-reel.mp4 / webm
        recorded_files = list(output_dir.glob("*.webm"))
        if recorded_files:
            latest_video = max(recorded_files, key=os.path.getctime)
            final_output = output_dir / "output-reel.webm"
            if final_output.exists():
                final_output.unlink()
            latest_video.rename(final_output)
            print(f"Cinematic video reel successfully rendered and saved to: {final_output}")

if __name__ == "__main__":
    print("Initializing Autonomous Cinematic Reel Engine...")
    hook_payload = generate_reel_hook()
    print("Generated Reel Hook Payload:", hook_payload)
    render_video_reel(hook_payload)
