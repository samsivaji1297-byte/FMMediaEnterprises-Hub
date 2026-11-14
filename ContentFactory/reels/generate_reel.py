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
            "point1": "WRITING EVERY POST MANUALLY",
            "point2": "ZERO DISTRIBUTION PIPELINES",
            "point3": "IGNORING AUTOMATION ARCHITECTURE",
            "footer": "COMMENT FM FOR THE WORKFLOW"
        },
        {
            "hook": "STOP WASTING 10 HOURS A WEEK ON CONTENT",
            "point1": "BUILD A 90-MINUTE ROUTINE",
            "point2": "LET PYTHON HANDLE THE HEAVY LIFTING",
            "point3": "DEPLOY REELS ON AUTOPILOT",
            "footer": "COMMENT FM FOR THE BLUEPRINT"
        },
        {
            "hook": "THE SYSTEM I USE TO RUN MY BUSINESS ON AUTO-PILOT",
            "point1": "PROGRAMMATIC SEO MATRIX",
            "point2": "HEADLESS API CONTENT FACTORY",
            "point3": "RECURSIVE CRON SCHEDULING",
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
      "point1": "{selected['point1']}",
      "point2": "{selected['point2']}",
      "point3": "{selected['point3']}",
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

    # Full-screen kinetic typography layout with zero boxed elements
    embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Kinetic Sovereign Reel Studio</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@700;900&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 1080px; height: 1920px; background: #000000 !important; color: #FFFFFF;
      display: flex; flex-direction: column; justify-content: center; align-items: center;
      position: relative; overflow: hidden; font-family: 'Inter', sans-serif;
      padding: 120px 80px; margin: 0; text-align: center;
      -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
    }}
    
    .vignette {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: radial-gradient(circle at center, rgba(20,20,25,1) 0%, rgba(0,0,0,1) 85%);
      z-index: 1; pointer-events: none;
    }}

    .stage {{
      position: relative; z-index: 3; width: 100%; height: 100%;
      display: flex; flex-direction: column; justify-content: center; align-items: center;
    }}

    @keyframes popIn {{
      0% {{ opacity: 0; transform: scale(0.92) translateY(20px); }}
      100% {{ opacity: 1; transform: scale(1) translateY(0); }}
    }}

    @keyframes fadeOut {{
      0% {{ opacity: 1; transform: scale(1); }}
      100% {{ opacity: 0; transform: scale(1.05); }}
    }}

    .kinetic-sequence {{
      position: absolute; width: 100%; opacity: 0;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
    }}

    /* Sequence Timing across 10 seconds */
    #seq-hook {{
      animation: popIn 0.4s ease forwards 0.2s, fadeOut 0.3s ease forwards 3.2s;
    }}
    #seq-point1 {{
      animation: popIn 0.4s ease forwards 3.5s, fadeOut 0.3s ease forwards 5.8s;
    }}
    #seq-point2 {{
      animation: popIn 0.4s ease forwards 6.1s, fadeOut 0.3s ease forwards 8.2s;
    }}
    #seq-point3 {{
      animation: popIn 0.4s ease forwards 8.4s;
    }}

    .badge-top {{
      font-size: 1.5rem; font-weight: 700; letter-spacing: 0.3em; color: #FF6B00;
      text-transform: uppercase; margin-bottom: 30px;
    }}

    .hero-text {{
      font-weight: 900; font-size: 5.2rem; line-height: 1.08; text-transform: uppercase;
      color: #FFFFFF; letter-spacing: -0.03em; max-width: 950px;
    }}

    .highlight {{
      color: #FF6B00;
    }}

    .footer-watermark {{
      position: absolute; bottom: 80px; left: 50%; transform: translateX(-50%);
      font-size: 1.2rem; font-weight: 700; letter-spacing: 0.3em; color: rgba(255,255,255,0.3);
      text-transform: uppercase; z-index: 4;
    }}
  </style>
</head>
<body>
  <div class="vignette"></div>
  
  <div class="stage">
    <!-- Hook Sequence -->
    <div class="kinetic-sequence" id="seq-hook">
      <div class="badge-top">// THE PROBLEM</div>
      <div class="hero-text">{content['hookText']}</div>
    </div>

    <!-- Point 1 -->
    <div class="kinetic-sequence" id="seq-point1">
      <div class="badge-top">01 / MISTAKE</div>
      <div class="hero-text">{content['point1']}</div>
    </div>

    <!-- Point 2 -->
    <div class="kinetic-sequence" id="seq-point2">
      <div class="badge-top">02 / MISTAKE</div>
      <div class="hero-text">{content['point2']}</div>
    </div>

    <!-- Point 3 -->
    <div class="kinetic-sequence" id="seq-point3">
      <div class="badge-top">03 / MISTAKE</div>
      <div class="hero-text">{content['point3']}</div>
    </div>
  </div>

  <div class="footer-watermark">{content['footerLabel']}</div>
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
        
        print("Capturing kinetic typography frames...")
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
            print(f"Kinetic sovereign reel successfully created: {final_output}")

if __name__ == "__main__":
    content_payload = generate_modular_reel_content()
    render_modular_reel(content_payload)
