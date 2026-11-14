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

def ensure_dependencies():
    """Ensure ffmpeg is available."""
    if not shutil.which("ffmpeg"):
        try:
            subprocess.run(["sudo", "apt-get", "update"], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True, stdout=subprocess.DEVNULL)
        except Exception:
            pass

def generate_modular_reel_content() -> dict:
    angles = [
        {
            "hook": "YOUR CONTENT ENGINE IS DRAINING YOUR TIME",
            "card1": "MANUAL WRITING KILLS SCALE",
            "card2": "ZERO DISTRIBUTION PIPELINES",
            "card3": "IGNORING ZERO-DEPENDENCY ARCHITECTURE",
            "footer": "COMMENT FM FOR THE WORKFLOW"
        },
        {
            "hook": "STOP WASTING 10 HOURS A WEEK ON CONTENT",
            "card1": "BUILD A 90-MINUTE AUTOMATION ROUTINE",
            "card2": "LET PYTHON HANDLE THE HEAVY LIFTING",
            "card3": "DEPLOY REELS ON AUTOPILOT",
            "footer": "COMMENT FM FOR THE BLUEPRINT"
        },
        {
            "hook": "THE EXACT SYSTEM I USE TO RUN MY BUSINESS ON AUTO-PILOT",
            "card1": "PROGRAMMATIC SEO & DATA MATRIX",
            "card2": "HEADLESS API CONTENT FACTORY",
            "card3": "RECURSIVE CRON SCHEDULING",
            "footer": "COMMENT FM FOR THE SYSTEM"
        }
    ]
    
    selected = random.choice(angles)
    
    prompt = f"""
    You are an elite social media growth architect. Create a dead-simple, highly engaging Instagram Reel script.
    The language MUST be basic, zero-jargon, and immediately understandable to anyone scrolling.
    
    Return ONLY valid JSON matching this exact structure with no extra markdown or fluff:
    {{
      "hookText": "{selected['hook']}",
      "card1": "{selected['card1']}",
      "card2": "{selected['card2']}",
      "card3": "{selected['card3']}",
      "footerLabel": "{selected['footer']}"
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

def generate_silent_audio(output_path: Path, duration_seconds: int = 10):
    """Generate a clean silent audio track via FFmpeg."""
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
        "-t", str(duration_seconds), str(output_path)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def render_modular_reel(content: dict):
    ensure_dependencies()
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    frames_dir = output_dir / 'frames'
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(exist_ok=True)
    
    total_seconds = 10.0
    audio_path = output_dir / 'silent_track.mp3'
    generate_silent_audio(audio_path, int(total_seconds))

    template_path = Path(__file__).parent / 'template.html'

    # Premium, elite dark-mode glassmorphic styling
    embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Elite Sovereign Reel Studio</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 1080px; height: 1920px; background: #070709 !important; color: #FFFFFF;
      display: flex; flex-direction: column; justify-content: space-between; align-items: center;
      position: relative; overflow: hidden; font-family: 'Plus Jakarta Sans', sans-serif;
      padding: 200px 70px 160px 70px; margin: 0;
      -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
    }}
    
    /* Ambient lighting layers for rich depth */
    .ambient-glow-1 {{
      position: absolute; top: -100px; left: 50%; transform: translateX(-50%);
      width: 800px; height: 800px; background: radial-gradient(circle, rgba(255,107,0,0.12) 0%, rgba(0,0,0,0) 70%);
      z-index: 1; pointer-events: none;
    }}
    .ambient-glow-2 {{
      position: absolute; bottom: -100px; left: 50%; transform: translateX(-50%);
      width: 800px; height: 800px; background: radial-gradient(circle, rgba(52,199,89,0.06) 0%, rgba(0,0,0,0) 70%);
      z-index: 1; pointer-events: none;
    }}
    .grid-pattern {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background-image: linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
      background-size: 50px 50px; z-index: 1; pointer-events: none;
    }}

    .content-wrapper {{
      position: relative; z-index: 3; width: 100%; height: 100%;
      display: flex; flex-direction: column; justify-content: space-between; align-items: center;
    }}

    /* Top Executive Header Card */
    .exec-header {{
      width: 100%; background: rgba(20, 20, 28, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08); border-top: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 20px; padding: 28px 36px; display: flex; flex-direction: column; gap: 12px;
      backdrop-filter: blur(20px); box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    }}
    .exec-badge-row {{
      display: flex; align-items: center; justify-content: space-between; width: 100%;
    }}
    .exec-tag {{
      font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 700;
      letter-spacing: 0.2em; color: #FF6B00; text-transform: uppercase;
    }}
    .exec-status-pill {{
      display: flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem; color: rgba(255,255,255,0.6); background: rgba(255,255,255,0.05);
      padding: 6px 14px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.08);
    }}
    .status-dot {{ width: 8px; height: 8px; background: #34C759; border-radius: 50%; box-shadow: 0 0 10px #34C759; }}
    
    .main-title {{
      font-weight: 800; font-size: 2.8rem; line-height: 1.15; text-transform: uppercase;
      color: #FFFFFF; letter-spacing: -0.02em;
    }}

    /* Sequential Glass Cards */
    .cards-container {{
      display: flex; flex-direction: column; gap: 24px; width: 100%; max-width: 940px;
      margin: auto 0;
    }}

    @keyframes revealCard {{
      0% {{ opacity: 0; transform: translateY(30px) scale(0.98); }}
      100% {{ opacity: 1; transform: translateY(0) scale(1); border-color: rgba(255, 107, 0, 0.4); box-shadow: 0 0 30px rgba(255, 107, 0, 0.12), 0 20px 40px rgba(0,0,0,0.5); }}
    }}

    .modular-card {{
      background: rgba(16, 16, 22, 0.75); border: 1px solid rgba(255, 255, 255, 0.08);
      border-top: 1px solid rgba(255, 255, 255, 0.15); backdrop-filter: blur(16px);
      border-radius: 20px; padding: 32px 36px; display: flex; align-items: center; gap: 28px;
      opacity: 0; transform: translateY(30px) scale(0.98);
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }}

    #card-1 {{ animation: revealCard 0.4s cubic-bezier(0.16, 1, 0.3, 1) 1.2s forwards; }}
    #card-2 {{ animation: revealCard 0.4s cubic-bezier(0.16, 1, 0.3, 1) 4.2s forwards; }}
    #card-3 {{ animation: revealCard 0.4s cubic-bezier(0.16, 1, 0.3, 1) 7.0s forwards; }}

    .card-badge {{
      width: 54px; height: 54px; border-radius: 14px; background: rgba(255, 107, 0, 0.15);
      border: 1px solid rgba(255, 107, 0, 0.4); display: flex; align-items: center; justify-content: center;
      font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 700; color: #FF6B00;
      flex-shrink: 0; box-shadow: 0 0 20px rgba(255, 107, 0, 0.2);
    }}
    .card-text {{
      font-weight: 800; font-size: 1.5rem; letter-spacing: -0.01em; color: #FFFFFF;
      text-transform: uppercase;
    }}

    /* Sleek Footer Signature */
    .footer-block {{
      width: 100%; display: flex; justify-content: space-between; align-items: center;
      border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 28px;
    }}
    .footer-brand {{
      font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; letter-spacing: 0.25em;
      color: #FF6B00; font-weight: 700; text-transform: uppercase;
    }}
    .footer-action {{
      font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; letter-spacing: 0.2em;
      color: rgba(255, 255, 255, 0.5); text-transform: uppercase;
    }}
  </style>
</head>
<body>
  <div class="ambient-glow-1"></div>
  <div class="ambient-glow-2"></div>
  <div class="grid-pattern"></div>
  
  <div class="content-wrapper">
    <div class="exec-header">
      <div class="exec-badge-row">
        <div class="exec-tag">// SYSTEM ARCHITECTURE</div>
        <div class="exec-status-pill">
          <div class="status-dot"></div> ACTIVE PIPELINE
        </div>
      </div>
      <div class="main-title">{content['hookText']}</div>
    </div>
    
    <div class="cards-container">
      <div class="modular-card" id="card-1">
        <div class="card-badge">01</div>
        <div class="card-text">{content['card1']}</div>
      </div>
      <div class="modular-card" id="card-2">
        <div class="card-badge">02</div>
        <div class="card-text">{content['card2']}</div>
      </div>
      <div class="modular-card" id="card-3">
        <div class="card-badge">03</div>
        <div class="card-text">{content['card3']}</div>
      </div>
    </div>
    
    <div class="footer-block">
      <div class="footer-brand">FM FRAMEWORKS</div>
      <div class="footer-action">{content['footerLabel']}</div>
    </div>
  </div>
</body>
</html>"""

    template_path.write_text(embedded_template, encoding='utf-8')

    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(viewport={'width': 1080, 'height': 1920})
        page = context.new_page()
        
        file_url = f"file://{template_path.resolve()}"
        page.goto(file_url, wait_until='networkidle')
        page.evaluate("document.fonts.ready")
        
        fps = 30
        total_frames = int(fps * total_seconds)
        interval = 1.0 / fps
        
        print("Capturing elite glassmorphic frames...")
        start_time = time.time()
        for i in range(total_frames):
            frame_path = frames_dir / f"frame_{i:04d}.png"
            page.screenshot(path=str(frame_path), type="png")
            
            target_elapsed = (i + 1) * interval
            actual_elapsed = time.time() - start_time
            if target_elapsed > actual_elapsed:
                time.sleep(target_elapsed - actual_elapsed)
                
        browser.close()
        
        video_only_output = output_dir / "temp_video.mp4"
        final_output = output_dir / "output-reel.mp4"
        ensure_dependencies()
        
        if shutil.which("ffmpeg"):
            print("Compiling frames into MP4 via FFmpeg...")
            ffmpeg_video_cmd = [
                "ffmpeg", "-y",
                "-framerate", str(fps),
                "-i", str(frames_dir / "frame_%04d.png"),
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-pix_fmt", "yuv420p",
                str(video_only_output)
            ]
            subprocess.run(ffmpeg_video_cmd, check=True)

            print("Muxing audio track with video...")
            ffmpeg_mux_cmd = [
                "ffmpeg", "-y",
                "-i", str(video_only_output),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                str(final_output)
            ]
            subprocess.run(ffmpeg_mux_cmd, check=True)
            print(f"Elite glassmorphic reel successfully created: {final_output}")

if __name__ == "__main__":
    content_payload = generate_modular_reel_content()
    render_modular_reel(content_payload)
