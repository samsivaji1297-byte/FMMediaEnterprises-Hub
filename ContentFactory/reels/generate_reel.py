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
    """Ensure ffmpeg and gTTS are available for audio generation."""
    if not shutil.which("ffmpeg"):
        try:
            subprocess.run(["sudo", "apt-get", "update"], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True, stdout=subprocess.DEVNULL)
        except Exception:
            pass
    try:
        import gtts
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "gtts"], check=True, stdout=subprocess.DEVNULL)

def generate_modular_reel_content() -> dict:
    angles = [
        {
            "hook": "3 REASONS YOUR CONTENT ENGINE IS DRAINING YOUR TIME",
            "card1": "1. WRITING EVERY SINGLE POST MANUALLY",
            "card2": "2. ZERO AUTOMATED DISTRIBUTION PIPELINES",
            "card3": "3. IGNORING ZERO-DEPENDENCY ARCHITECTURE",
            "footer": "COMMENT FM FOR THE WORKFLOW",
            "spoken": "Three reasons your content engine is draining your time. First, writing every single post manually. Second, having zero automated distribution pipelines. And third, ignoring zero dependency architecture. Comment FM for the workflow."
        },
        {
            "hook": "HOW TO STOP WASTING 10 HOURS A WEEK ON CONTENT",
            "card1": "1. BUILD A 90-MINUTE AUTOMATION ROUTINE",
            "card2": "2. LET PYTHON HANDLE THE HEAVY LIFTING",
            "card3": "3. DEPLOY REELS ON AUTOPILOT",
            "footer": "COMMENT FM FOR THE BLUEPRINT",
            "spoken": "How to stop wasting ten hours a week on content. First, build a ninety minute automation routine. Second, let Python handle the heavy lifting. Third, deploy reels on autopilot. Comment FM for the blueprint."
        },
        {
            "hook": "THE EXACT SYSTEM I USE TO RUN MY BUSINESS ON AUTO-PILOT",
            "card1": "1. PROGRAMMATIC SEO & DATA MATRIX",
            "card2": "2. HEADLESS API CONTENT FACTORY",
            "card3": "3. RECURSIVE CRON SCHEDULING",
            "footer": "COMMENT FM FOR THE SYSTEM",
            "spoken": "The exact system I use to run my business on autopilot. First, programmatic SEO and data matrices. Second, a headless API content factory. Third, recursive cron scheduling. Comment FM for the system."
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
      "footerLabel": "{selected['footer']}",
      "spoken": "{selected['spoken']}"
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

def synthesize_voiceover(text: str, output_path: Path):
    """Generate voiceover using gTTS."""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', tld='com', slow=False)
        tts.save(str(output_path))
        print(f"Voiceover successfully synthesized: {output_path}")
    except Exception as e:
        print(f"Voiceover generation fallback triggered: {e}")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", 
            "-t", "8", str(output_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def render_modular_reel(content: dict):
    ensure_dependencies()
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    frames_dir = output_dir / 'frames'
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(exist_ok=True)
    
    audio_path = output_dir / 'voiceover.mp3'
    synthesize_voiceover(content['spoken'], audio_path)

    template_path = Path(__file__).parent / 'template.html'

    # Clean HTML template using pure CSS keyframe animations for deterministic frame rendering
    embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Deterministic Sovereign Reel Studio</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Inter:wght@400;600;800;900&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 1080px; height: 1920px; background: #030305 !important; color: #FFFFFF;
      display: flex; flex-direction: column; justify-content: space-between; align-items: center;
      position: relative; overflow: hidden; font-family: 'JetBrains Mono', monospace, sans-serif;
      padding: 160px 70px 120px 70px; margin: 0;
      -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
    }}
    .ambient-glow-top {{
      position: absolute; top: -150px; left: 50%; transform: translateX(-50%);
      width: 900px; height: 900px; background: radial-gradient(circle, rgba(255,107,0,0.15) 0%, rgba(0,0,0,0) 70%);
      z-index: 1; pointer-events: none;
    }}
    .grid-overlay {{
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
      background-size: 60px 60px; z-index: 1; pointer-events: none;
    }}
    .content-wrapper {{
      position: relative; z-index: 3; width: 100%; height: 100%;
      display: flex; flex-direction: column; justify-content: space-between; align-items: center;
    }}
    
    .visual-mockup-container {{
      width: 100%; height: 300px; background: rgba(15, 15, 20, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 24px;
      backdrop-filter: blur(20px); display: flex; flex-direction: column;
      overflow: hidden; box-shadow: 0 25px 60px rgba(0,0,0,0.8);
      margin-bottom: 20px;
    }}
    .mockup-header {{
      background: rgba(25, 25, 35, 0.9); padding: 14px 24px;
      display: flex; align-items: center; justify-content: space-between;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .mockup-dots {{ display: flex; gap: 8px; }}
    .mockup-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
    .dot-red {{ background: #FF5F56; }}
    .dot-yellow {{ background: #FFBD2E; }}
    .dot-green {{ background: #27C93F; }}
    .mockup-url {{ font-size: 0.9rem; color: rgba(255,255,255,0.5); letter-spacing: 0.1em; }}
    .mockup-body {{
      flex: 1; display: flex; align-items: center; justify-content: center;
      padding: 20px; font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.6rem;
      color: #FF6B00; text-transform: uppercase; letter-spacing: -0.02em; text-align: center;
      background: radial-gradient(circle at center, rgba(255,107,0,0.08) 0%, transparent 70%);
    }}

    .header-block {{
      display: flex; flex-direction: column; align-items: center; text-align: center; width: 100%;
      margin-bottom: 10px;
    }}
    .main-title {{
      font-family: 'Inter', sans-serif; font-weight: 900; font-size: 3.0rem;
      line-height: 1.15; text-transform: uppercase; color: #FFFFFF;
      letter-spacing: -0.03em; text-shadow: 0 10px 30px rgba(0,0,0,0.9);
    }}
    
    .cards-container {{
      display: flex; flex-direction: column; gap: 20px; width: 100%; max-width: 940px;
      margin: auto 0;
    }}

    /* Deterministic Keyframe Animations */
    @keyframes revealCard {{
      0% {{ opacity: 0; transform: translateY(35px) scale(0.98); }}
      100% {{ opacity: 1; transform: translateY(0) scale(1); border-color: rgba(255, 107, 0, 0.4); box-shadow: 0 0 35px rgba(255, 107, 0, 0.15), 0 20px 50px rgba(0,0,0,0.7); }}
    }}

    .modular-card {{
      background: rgba(18, 18, 24, 0.8); border: 1px solid rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(16px); border-radius: 20px; padding: 28px 34px;
      display: flex; align-items: center; gap: 28px;
      opacity: 0; transform: translateY(35px) scale(0.98);
      box-shadow: 0 20px 50px rgba(0,0,0,0.7);
    }}

    #card-1 {{ animation: revealCard 0.4s cubic-bezier(0.16, 1, 0.3, 1) 1.0s forwards; }}
    #card-2 {{ animation: revealCard 0.4s cubic-bezier(0.16, 1, 0.3, 1) 3.2s forwards; }}
    #card-3 {{ animation: revealCard 0.4s cubic-bezier(0.16, 1, 0.3, 1) 5.4s forwards; }}

    .badge-icon {{
      width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
      font-size: 1.5rem; font-weight: 800; flex-shrink: 0; font-family: 'Inter', sans-serif;
    }}
    .badge-red {{ background: rgba(255, 59, 48, 0.18); color: #FF3B30; border: 1px solid rgba(255, 59, 48, 0.5); }}
    .badge-amber {{ background: rgba(255, 107, 0, 0.18); color: #FF6B00; border: 1px solid rgba(255, 107, 0, 0.5); }}
    .badge-green {{ background: rgba(52, 199, 89, 0.18); color: #34C759; border: 1px solid rgba(52, 199, 89, 0.5); }}
    .card-text {{
      font-family: 'Inter', sans-serif; font-size: 1.35rem; font-weight: 800;
      letter-spacing: -0.01em; color: #FFFFFF; text-transform: uppercase;
    }}
    
    .footer-block {{
      display: flex; justify-content: space-between; align-items: center; width: 100%;
      border-top: 1px solid rgba(255, 255, 255, 0.15); padding-top: 20px; margin-top: 10px;
    }}
    .footer-label {{ font-size: 1.05rem; letter-spacing: 0.2em; color: #FF6B00; font-weight: 800; text-transform: uppercase; }}
    .cta-link {{ font-size: 1.05rem; letter-spacing: 0.25em; color: rgba(255,255,255,0.8); font-weight: 700; text-transform: uppercase; }}
  </style>
</head>
<body>
  <div class="ambient-glow-top"></div>
  <div class="grid-overlay"></div>
  
  <div class="content-wrapper">
    <div class="visual-mockup-container">
      <div class="mockup-header">
        <div class="mockup-dots">
          <div class="mockup-dot dot-red"></div>
          <div class="mockup-dot dot-yellow"></div>
          <div class="mockup-dot dot-green"></div>
        </div>
        <div class="mockup-url">system://matrix/execution_core</div>
      </div>
      <div class="mockup-body">AUTOMATED PIPELINE MATRIX ACTIVE</div>
    </div>

    <div class="header-block">
      <div class="main-title">{content['hookText']}</div>
    </div>
    
    <div class="cards-container">
      <div class="modular-card" id="card-1">
        <div class="badge-icon badge-red">1</div>
        <div class="card-text">{content['card1']}</div>
      </div>
      <div class="modular-card" id="card-2">
        <div class="badge-icon badge-amber">2</div>
        <div class="card-text">{content['card2']}</div>
      </div>
      <div class="modular-card" id="card-3">
        <div class="badge-icon badge-green">3</div>
        <div class="card-text">{content['card3']}</div>
      </div>
    </div>
    
    <div class="footer-block">
      <div class="footer-label">{content['footerLabel']}</div>
      <div class="cta-link">FMFRAMEWORKS</div>
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
        total_seconds = 8.0
        total_frames = int(fps * total_seconds)
        interval = 1.0 / fps
        
        print("Capturing deterministic sovereign-grade frames...")
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
            print(f"Deterministic sovereign reel successfully created: {final_output}")

if __name__ == "__main__":
    content_payload = generate_modular_reel_content()
    render_modular_reel(content_payload)
