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
            "card1": "01 / MANUAL WRITING",
            "card2": "02 / ZERO DISTRIBUTION PIPELINES",
            "card3": "03 / NO ZERO-DEPENDENCY ARCHITECTURE",
            "footer": "COMMENT FM FOR THE WORKFLOW"
        },
        {
            "hook": "STOP WASTING 10 HOURS A WEEK ON CONTENT",
            "card1": "01 / 90-MINUTE AUTOMATION ROUTINE",
            "card2": "02 / PYTHON HANDLES THE HEAVY LIFTING",
            "card3": "03 / DEPLOY REELS ON AUTOPILOT",
            "footer": "COMMENT FM FOR THE BLUEPRINT"
        },
        {
            "hook": "THE EXACT SYSTEM I USE TO RUN MY BUSINESS ON AUTO-PILOT",
            "card1": "01 / PROGRAMMATIC SEO MATRIX",
            "card2": "02 / HEADLESS API FACTORY",
            "card3": "03 / RECURSIVE CRON SCHEDULING",
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
    """Generate a clean, reliable silent audio track via FFmpeg to guarantee zero network/TTS dropouts."""
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
    
    # Use a fixed 10-second duration for smooth, un-rushed reading pacing
    total_seconds = 10.0
    audio_path = output_dir / 'silent_track.mp3'
    generate_silent_audio(audio_path, int(total_seconds))

    template_path = Path(__file__).parent / 'template.html'

    # High-contrast, clean minimalist typographic layout with perfectly timed keyframes
    embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Stable Sovereign Reel Studio</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Inter:wght@400;700;900&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 1080px; height: 1920px; background: #000000 !important; color: #FFFFFF;
      display: flex; flex-direction: column; justify-content: space-between; align-items: center;
      position: relative; overflow: hidden; font-family: 'Inter', sans-serif;
      padding: 240px 90px 200px 90px; margin: 0;
      -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
    }}
    
    .ambient-glow {{
      position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
      width: 800px; height: 800px; background: radial-gradient(circle, rgba(255,107,0,0.1) 0%, rgba(0,0,0,0) 70%);
      z-index: 1; pointer-events: none;
    }}

    .content-wrapper {{
      position: relative; z-index: 3; width: 100%; height: 100%;
      display: flex; flex-direction: column; justify-content: space-between; align-items: center;
      text-align: center;
    }}

    .hook-block {{
      width: 100%;
      display: flex; flex-direction: column; align-items: center; gap: 24px;
    }}
    .hook-tag {{
      font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700;
      letter-spacing: 0.3em; color: #FF6B00; text-transform: uppercase;
    }}
    .main-title {{
      font-weight: 900; font-size: 4.5rem; line-height: 1.12; text-transform: uppercase;
      color: #FFFFFF; letter-spacing: -0.03em; max-width: 920px;
    }}

    .points-container {{
      display: flex; flex-direction: column; gap: 45px; width: 100%; max-width: 900px;
      margin: auto 0;
    }}

    @keyframes fadeInText {{
      0% {{ opacity: 0; transform: translateY(25px); }}
      100% {{ opacity: 1; transform: translateY(0); }}
    }}

    .minimal-point {{
      font-family: 'JetBrains Mono', monospace; font-size: 2.3rem; font-weight: 700;
      color: #F0F0F0; text-transform: uppercase; letter-spacing: -0.02em;
      opacity: 0; transform: translateY(25px); text-align: left;
      padding-left: 35px; border-left: 5px solid #FF6B00;
    }}

    #point-1 {{ animation: fadeInText 0.4s ease forwards 1.5s; }}
    #point-2 {{ animation: fadeInText 0.4s ease forwards 4.5s; }}
    #point-3 {{ animation: fadeInText 0.4s ease forwards 7.2s; }}

    .footer-block {{
      width: 100%; display: flex; flex-direction: column; align-items: center; gap: 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.12); padding-top: 35px;
    }}
    .footer-label {{
      font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; letter-spacing: 0.25em;
      color: #FF6B00; font-weight: 700; text-transform: uppercase;
    }}
    .footer-sub {{
      font-size: 1.05rem; letter-spacing: 0.2em; color: rgba(255, 255, 255, 0.4); text-transform: uppercase;
    }}
  </style>
</head>
<body>
  <div class="ambient-glow"></div>
  
  <div class="content-wrapper">
    <div class="hook-block">
      <div class="hook-tag">// SYSTEM PROTOCOL</div>
      <div class="main-title">{content['hookText']}</div>
    </div>
    
    <div class="points-container">
      <div class="minimal-point" id="point-1">{content['card1']}</div>
      <div class="minimal-point" id="point-2">{content['card2']}</div>
      <div class="minimal-point" id="point-3">{content['card3']}</div>
    </div>
    
    <div class="footer-block">
      <div class="footer-label">{content['footerLabel']}</div>
      <div class="footer-sub">FM FRAMEWORKS</div>
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
        
        print("Capturing stable sovereign frames...")
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

            print("Muxing stable audio track with video...")
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
            print(f"Stable sovereign reel successfully created: {final_output}")

if __name__ == "__main__":
    content_payload = generate_modular_reel_content()
    render_modular_reel(content_payload)
