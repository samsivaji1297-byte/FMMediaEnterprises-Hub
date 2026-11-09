import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import json
import os
import random
import shutil
import subprocess
import time
from playwright.sync_api import sync_playwright
from config import get_client, get_groq_client, call_with_fallback, DEFAULT_HYBRID_CASCADE

def ensure_ffmpeg():
    if not shutil.which("ffmpeg"):
        try:
            subprocess.run(["sudo", "apt-get", "update"], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True, stdout=subprocess.DEVNULL)
        except Exception:
            pass

def generate_modular_reel_content() -> dict:
    topics = [
        "Autonomous pSEO data matrix compilation and GitHub Pages deployment",
        "Headless Meta Graph API short-form video distribution pipelines",
        "Operator mindset systems, workflow compression, and sovereign asset design",
        "Zero-dependency single-file web applications and local storage synchronization"
    ]
    selected_topic = random.choice(topics)

    prompt = f"""
    You are an elite direct-response system architect crafting a high-retention modular framework Instagram Reel script.
    
    Current Architectural Focus: {selected_topic}
    Product Context: fmframeworks.gumroad.com ('The Compression System', 'Operator Mindset Kit').
    
    CORE DESIGN & COPYWRITING MANDATE:
    - Deliver absolute clarity, structural leverage, and mimetic dopamine hits.
    - Provide 3 distinct modular framework points representing a sovereign pipeline based on the focus above.
    - Ensure the copy is completely fresh, punchy, and highly specific.
    
    Return ONLY valid JSON matching this exact structure with no extra markdown or fluff:
    {{
      "mainHeader": "SHORT PUNCHY TITLE ABOUT THE SYSTEM",
      "card1": "1. FIRST MODULE STEP OR METRIC",
      "card2": "2. SECOND MODULE STEP OR METRIC",
      "card3": "3. THIRD MODULE STEP OR PAYOFF",
      "footerLabel": "SYSTEM ARCHITECTURE"
    }}
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
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    template_path = Path(__file__).parent / 'template.html'

    # Forced pure black root styling to eliminate the initial white frame flash
    embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Modular Framework IG Reel Studio</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Inter:wght@400;600;800&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 1080px; height: 1920px; background: #000000 !important; color: #FFFFFF;
      display: flex; flex-direction: column; justify-content: space-between; align-items: center;
      position: relative; overflow: hidden; font-family: 'JetBrains Mono', monospace;
      padding: 260px 80px 140px 80px; margin: 0;
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
      font-family: 'Inter', sans-serif; font-weight: 800; font-size: 3.5rem;
      line-height: 1.15; text-transform: uppercase; color: #FFFFFF;
      letter-spacing: -0.02em; margin-bottom: 20px; text-shadow: 0 4px 20px rgba(0,0,0,0.8);
    }}
    .arrow-icon {{
      font-size: 2.8rem; color: #FFFFFF; margin-top: 5px; animation: bounce 1.5s infinite ease-in-out;
    }}
    @keyframes bounce {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(10px); }}
    }}
    .cards-container {{
      display: flex; flex-direction: column; gap: 26px; width: 100%; max-width: 920px;
      margin: auto 0;
    }}
    .modular-card {{
      background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(12px); border-radius: 16px; padding: 34px 38px;
      display: flex; align-items: center; gap: 32px;
      opacity: 0; transform: translateY(30px); transition: opacity 0.5s ease, transform 0.5s ease;
      box-shadow: 0 12px 40px rgba(0,0,0,0.6);
    }}
    .modular-card.visible {{
      opacity: 1; transform: translateY(0);
    }}
    .badge-icon {{
      width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
      font-size: 1.7rem; font-weight: 700; flex-shrink: 0;
    }}
    .badge-red {{ background: rgba(255, 59, 48, 0.15); color: #FF3B30; border: 1px solid rgba(255, 59, 48, 0.4); box-shadow: 0 0 25px rgba(255, 59, 48, 0.3); }}
    .badge-amber {{ background: rgba(255, 107, 0, 0.15); color: #FF6B00; border: 1px solid rgba(255, 107, 0, 0.4); box-shadow: 0 0 25px rgba(255, 107, 0, 0.3); }}
    .badge-green {{ background: rgba(52, 199, 89, 0.15); color: #34C759; border: 1px solid rgba(52, 199, 89, 0.4); box-shadow: 0 0 25px rgba(52, 199, 89, 0.3); }}
    .card-text {{
      font-family: 'Inter', sans-serif; font-size: 1.45rem; font-weight: 700;
      letter-spacing: -0.01em; color: #FFFFFF; text-transform: uppercase;
    }}
    .footer-block {{
      display: flex; justify-content: space-between; align-items: center; width: 100%;
      border-top: 1px solid rgba(255, 255, 255, 0.15); padding-top: 26px;
    }}
    .footer-label {{
      font-size: 1.05rem; letter-spacing: 0.25em; color: rgba(255, 255, 255, 0.5); text-transform: uppercase;
    }}
    .cta-link {{
      font-size: 1.1rem; letter-spacing: 0.25em; color: #FF6B00; font-weight: 700; text-transform: uppercase;
    }}
  </style>
</head>
<body style="background: #000000;">
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

    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox', '--force-dark-mode'])
        context = browser.new_context(
            viewport={'width': 1080, 'height': 1920},
            record_video_dir=str(output_dir),
            record_video_size={'width': 1080, 'height': 1920}
        )
        
        page = context.new_page()
        page.evaluate("() => document.body.style.backgroundColor = '#000000'")
        file_url = f"file://{template_path.resolve()}"
        page.goto(file_url, wait_until='networkidle')
        page.evaluate("document.fonts.ready")
        
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
            
            final_output = output_dir / "output-reel.mp4"
            ensure_ffmpeg()
            
            if shutil.which("ffmpeg"):
                # Bulletproof audio muxing filter chain
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-i", str(raw_output),
                    "-f", "lavfi", "-i", "sine=frequency=55:duration=8.0",
                    "-f", "lavfi", "-i", "anoisesrc=d=8.0:c=pink:r=44100:a=0.015",
                    "-filter_complex",
                    "[1:a]volume=0.12,lowpass=f=220[drone];"
                    "[2:a]volume=0.03,highpass=f=1200[texture];"
                    "[drone][texture]amix=inputs=2[mix];"
                    "[mix]asetpts=PTS-STARTPTS[audio]",
                    "-map", "0:v", "-map", "[audio]",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "128k",
                    "-pix_fmt", "yuv420p", "-shortest",
                    str(final_output)
                ]
                subprocess.run(ffmpeg_cmd, check=True)

if __name__ == "__main__":
    content_payload = generate_modular_reel_content()
    render_modular_reel(content_payload)
