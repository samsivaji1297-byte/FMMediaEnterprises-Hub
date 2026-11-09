import sys
from pathlib import Path

# Automatically inject repository root into sys.path so config.py loads cleanly
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import json
import os
import shutil
import subprocess
import time
from playwright.sync_api import sync_playwright
from config import get_client, get_groq_client, call_with_fallback, DEFAULT_HYBRID_CASCADE

def ensure_ffmpeg():
    """Checks if ffmpeg is available, and installs it via apt if running on Linux without it."""
    if not shutil.which("ffmpeg"):
        print("FFmpeg not found in PATH. Attempting automated installation...")
        try:
            subprocess.run(["sudo", "apt-get", "update"], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True, stdout=subprocess.DEVNULL)
            print("FFmpeg installed successfully.")
        except Exception as e:
            print(f"Warning: Could not auto-install ffmpeg ({e}).")

def generate_modular_reel_content() -> dict:
    """Queries AI models for a 3-part modular framework script matching elite high-retention reel layouts."""
    prompt = """
    You are an elite direct-response system architect crafting a high-retention modular framework Instagram Reel script.
    
    Product & Framework Context:
    Digital operational frameworks (fmframeworks.gumroad.com), including 'The Compression System', 
    'Operator Mindset Kit', and the '90-Minute Protocol'.
    
    CORE DESIGN & COPYWRITING MANDATE:
    - Deliver absolute clarity, structural leverage, and mimetic dopamine hits. Make the viewer feel instantly in command.
    - Provide 3 distinct modular framework points that represent a sovereign pipeline.
    
    Return ONLY valid JSON matching this exact structure with no extra markdown or fluff:
    {
      "mainHeader": "THE ULTIMATE AUTOMATION FORMAT",
      "card1": "1. 90-MINUTE COMPRESSION PROTOCOL",
      "card2": "2. HEADLESS PLAYWRIGHT PIPELINES",
      "card3": "3. AUTONOMOUS META API PUBLISHING",
      "footerLabel": "SYSTEM ARCHITECTURE"
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

def render_modular_reel(content: dict):
    """Renders visual via Playwright and muxes ambient sound into an MP4 container via FFmpeg."""
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    template_path = Path(__file__).parent / 'template.html'

    embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Modular Framework IG Reel Studio</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Inter:wght@400;600;800&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      width: 1080px; height: 1920px; background: #000000; color: #FFFFFF;
      display: flex; flex-direction: column; justify-content: space-between; align-items: center;
      position: relative; overflow: hidden; font-family: 'JetBrains Mono', monospace;
      padding: 140px 80px;
      -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
    }}
    .grid-overlay {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
      background-size: 60px 60px; z-index: 1; pointer-events: none;
    }}
    .scanline {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.3) 50%);
      background-size: 100% 4px; z-index: 2; pointer-events: none;
    }}
    .content-wrapper {{
      position: relative; z-index: 3; width: 100%; height: 100%;
      display: flex; flex-direction: column; justify-content: space-between; align-items: center;
    }}
    .header-block {{
      display: flex; flex-direction: column; align-items: center; text-align: center; width: 100%;
    }}
    .main-title {{
      font-family: 'Inter', sans-serif; font-weight: 800; font-size: 3.8rem;
      line-height: 1.15; text-transform: uppercase; color: #FFFFFF;
      letter-spacing: -0.02em; margin-bottom: 24px; text-shadow: 0 4px 20px rgba(0,0,0,0.8);
    }}
    .arrow-icon {{
      font-size: 3rem; color: #FFFFFF; margin-top: 10px; animation: bounce 1.5s infinite ease-in-out;
    }}
    @keyframes bounce {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(12px); }}
    }}
    .cards-container {{
      display: flex; flex-direction: column; gap: 28px; width: 100%; max-width: 920px;
      margin: auto 0;
    }}
    .modular-card {{
      background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(12px); border-radius: 16px; padding: 36px 40px;
      display: flex; align-items: center; gap: 32px;
      opacity: 0; transform: translateY(30px); transition: opacity 0.5s ease, transform 0.5s ease;
      box-shadow: 0 12px 40px rgba(0,0,0,0.6);
    }}
    .modular-card.visible {{
      opacity: 1; transform: translateY(0);
    }}
    .badge-icon {{
      width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
      font-size: 1.8rem; font-weight: 700; flex-shrink: 0;
    }}
    .badge-red {{ background: rgba(255, 59, 48, 0.15); color: #FF3B30; border: 1px solid rgba(255, 59, 48, 0.4); box-shadow: 0 0 25px rgba(255, 59, 48, 0.3); }}
    .badge-amber {{ background: rgba(255, 107, 0, 0.15); color: #FF6B00; border: 1px solid rgba(255, 107, 0, 0.4); box-shadow: 0 0 25px rgba(255, 107, 0, 0.3); }}
    .badge-green {{ background: rgba(52, 199, 89, 0.15); color: #34C759; border: 1px solid rgba(52, 199, 89, 0.4); box-shadow: 0 0 25px rgba(52, 199, 89, 0.3); }}
    .card-text {{
      font-family: 'Inter', sans-serif; font-size: 1.6rem; font-weight: 700;
      letter-spacing: -0.01em; color: #FFFFFF; text-transform: uppercase;
    }}
    .footer-block {{
      display: flex; justify-content: space-between; align-items: center; width: 100%;
      border-top: 1px solid rgba(255, 255, 255, 0.15); padding-top: 28px;
    }}
    .footer-label {{
      font-size: 1.1rem; letter-spacing: 0.25em; color: rgba(255, 255, 255, 0.5); text-transform: uppercase;
    }}
    .cta-link {{
      font-size: 1.15rem; letter-spacing: 0.25em; color: #FF6B00; font-weight: 700; text-transform: uppercase;
    }}
  </style>
</head>
<body>
  <div class="grid-overlay"></div>
  <div class="scanline"></div>
  
  <div class="content-wrapper">
    <div class="header-block">
      <div class="main-title">{content['mainHeader']}</div>
      <div class="arrow-icon">↓</div>
    </div>
    
    <div class="cards-container">
      <div class="modular-card" id="card-1">
        <div class="badge-icon badge-red">∞</div>
        <div class="card-text">{content['card1']}</div>
      </div>
      <div class="modular-card" id="card-2">
        <div class="badge-icon badge-amber">α</div>
        <div class="card-text">{content['card2']}</div>
      </div>
      <div class="modular-card" id="card-3">
        <div class="badge-icon badge-green">✓</div>
        <div class="card-text">{content['card3']}</div>
      </div>
    </div>
    
    <div class="footer-block">
      <div class="footer-label">{content['footerLabel']}</div>
      <div class="cta-link">→ FMFRAMEWORKS.GUMROAD.COM</div>
    </div>
  </div>

  <script>
    window.addEventListener('DOMContentLoaded', () => {{
      setTimeout(() => {{ document.getElementById('card-1').classList.add('visible'); }}, 800);
      setTimeout(() => {{ document.getElementById('card-2').classList.add('visible'); }}, 2400);
      setTimeout(() => {{ document.getElementById('card-3').classList.add('visible'); }}, 4000);
    }});
  </script>
</body>
</html>"""

    template_path.write_text(embedded_template, encoding='utf-8')

    print("Launching Playwright Modular Framework recorder...")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(
            viewport={'width': 1080, 'height': 1920},
            record_video_dir=str(output_dir),
            record_video_size={'width': 1080, 'height': 1920}
        )
        
        page = context.new_page()
        file_url = f"file://{template_path.resolve()}"
        page.goto(file_url, wait_until='networkidle')
        page.evaluate("document.fonts.ready")
        
        print("Recording 8-second visual reel session...")
        time.sleep(8.0)
        
        context.close()
        browser.close()
        
        recorded_files = list(output_dir.glob("*.webm"))
        if recorded_files:
            latest_video = max(recorded_files, key=os.path.getctime)
            raw_output = output_dir / "raw-reel.webm"
            if raw_output.exists():
                raw_output.unlink()
            latest_video.rename(raw_output)
            
            # Target MP4 output so AAC audio muxing is fully supported by the container
            final_output = output_dir / "output-reel.mp4"
            
            ensure_ffmpeg()
            
            if shutil.which("ffmpeg"):
                print("Muxing ambient sub-bass drone soundtrack into MP4 container via FFmpeg...")
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-i", str(raw_output),
                    "-f", "lavfi", "-i", "sine=frequency=55:duration=8.0",
                    "-filter_complex", "[1:a]volume=0.12[a];[a]lowpass=f=300[audio]",
                    "-map", "0:v", "-map", "[audio]",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "128k",
                    "-pix_fmt", "yuv420p", "-shortest",
                    str(final_output)
                ]
                subprocess.run(ffmpeg_cmd, check=True)
                print(f"Audio-muxed modular MP4 reel successfully rendered: {final_output}")
            else:
                print("FFmpeg unavailable.")

if __name__ == "__main__":
    print("Initializing Modular Framework Autonomous Reel Engine with Ambient Sound...")
    content_payload = generate_modular_reel_content()
    print("Modular Payload:", content_payload)
    render_modular_reel(content_payload)
