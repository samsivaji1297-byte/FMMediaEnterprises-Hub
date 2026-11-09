import sys
from pathlib import Path

# Automatically inject repository root into sys.path so config.py loads cleanly
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import json
import os
import time
from playwright.sync_api import sync_playwright
from config import get_client, get_groq_client, call_with_fallback, DEFAULT_HYBRID_CASCADE

def generate_terminal_reel_hook() -> dict:
    """Queries AI models using modular bracket architectures for high-retention Terminal Brutalist reels."""
    prompt = """
    You are an elite direct-response system architect crafting a high-status Terminal Brutalist Instagram Reel hook.
    
    Product & Framework Context:
    Digital operational frameworks (fmframeworks.gumroad.com), including 'The Compression System', 
    'Operator Mindset Kit', and the '90-Minute Protocol'.
    
    CORE DESIGN & COPYWRITING MANDATE:
    - Focus on structural clarity, hidden mechanisms, and unlocked capabilities. Never use fear-based hooks.
    - Use modular bracket structures (e.g., [THING], [SYSTEM], [PROTOCOL]) that signal precision and data architecture.
    
    Return ONLY valid JSON matching this exact structure with no extra markdown or fluff:
    {
      "badge": "SYS.PROTOCOL // 01",
      "mainText": "THERE'S A [SYSTEM]<br>HIDING INSIDE<br>YOUR [WORKFLOW]",
      "subText": "COMPRESS WEEKS OF EXECUTION INTO 90 MINUTES"
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

def render_terminal_reel(hook_data: dict):
    """Renders a 1080x1920 Terminal Brutalist reel with Web Audio API synthesis via Playwright."""
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    template_path = Path(__file__).parent / 'template.html'

    embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Terminal Brutalist IG Reel Studio</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&family=Inter:wght@400;600;800&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      width: 1080px; height: 1920px; background: #000000; color: #FFFFFF;
      display: flex; flex-direction: column; justify-content: space-between; align-items: flex-start;
      position: relative; overflow: hidden; font-family: 'JetBrains Mono', monospace;
      padding: 120px 90px;
      -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
    }}
    /* Swiss Grid & Scanline Overlay */
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
    .content-container {{
      position: relative; z-index: 3; width: 100%; height: 100%;
      display: flex; flex-direction: column; justify-content: space-between;
    }}
    .header-block {{
      display: flex; justify-content: space-between; align-items: center;
      border-bottom: 1px solid rgba(255, 255, 255, 0.2); padding-bottom: 24px;
      width: 100%;
    }}
    .badge {{
      font-size: 1.1rem; letter-spacing: 0.25em; color: #FF6B00; font-weight: 700;
      text-transform: uppercase;
    }}
    .timestamp {{
      font-size: 1rem; letter-spacing: 0.15em; color: rgba(255, 255, 255, 0.4);
    }}
    .main-hook {{
      font-family: 'Inter', sans-serif; font-weight: 800; font-size: 4.8rem;
      line-height: 1.1; text-transform: uppercase; color: #FFFFFF;
      letter-spacing: -0.02em; margin: auto 0;
    }}
    .main-hook span {{
      color: #FF6B00;
    }}
    .footer-block {{
      display: flex; flex-direction: column; gap: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.2); padding-top: 32px;
      width: 100%;
    }}
    .sub-text {{
      font-size: 1.25rem; font-weight: 500; letter-spacing: 0.2em;
      text-transform: uppercase; color: rgba(255, 255, 255, 0.85);
    }}
    .cta-link {{
      font-size: 1.1rem; letter-spacing: 0.25em; color: #FF6B00; font-weight: 700;
      text-transform: uppercase;
    }}
    .cursor {{
      display: inline-block; width: 16px; height: 36px; background: #FF6B00;
      vertical-align: middle; animation: blink 1s infinite; margin-left: 8px;
    }}
    @keyframes blink {{
      0%, 50% {{ opacity: 1; }}
      51%, 100% {{ opacity: 0; }}
    }}
  </style>
</head>
<body>
  <div class="grid-overlay"></div>
  <div class="scanline"></div>
  
  <div class="content-container">
    <div class="header-block">
      <div class="badge">{hook_data['badge']}</div>
      <div class="timestamp">FM.ENGINE // SECURE</div>
    </div>
    
    <div class="main-hook">
      {hook_data['mainText']}<span class="cursor"></span>
    </div>
    
    <div class="footer-block">
      <div class="sub-text">{hook_data['subText']}</div>
      <div class="cta-link">→ FMFRAMEWORKS.GUMROAD.COM</div>
    </div>
  </div>

  <script>
    // In-House Web Audio API Sound Design Synthesizer
    window.addEventListener('DOMContentLoaded', () => {{
      try {{
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        const ctx = new AudioContext();
        
        // Low Sub-Bass Drone Atmosphere
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(55, ctx.currentTime); // A1 note
        
        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 5.5);
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.start();
        osc.stop(ctx.currentTime + 6.0);
        
        // Mechanical UI Click Transient
        setTimeout(() => {{
          const clickOsc = ctx.createOscillator();
          const clickGain = ctx.createGain();
          clickOsc.type = 'square';
          clickOsc.frequency.setValueAtTime(800, ctx.currentTime);
          clickGain.gain.setValueAtTime(0.05, ctx.currentTime);
          clickGain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
          clickOsc.connect(clickGain);
          clickGain.connect(ctx.destination);
          clickOsc.start();
          clickOsc.stop(ctx.currentTime + 0.05);
        }, 150);
      }} catch(e) {{
        console.log('Audio Context suppressed');
      }}
    }});
  </script>
</body>
</html>"""

    template_path.write_text(embedded_template, encoding='utf-8')

    print("Launching Playwright Terminal recorder...")
    with sync_playwright() as p:
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
        
        print("Recording 6-second Terminal Brutalist reel session...")
        time.sleep(6.0)
        
        context.close()
        browser.close()
        
        recorded_files = list(output_dir.glob("*.webm"))
        if recorded_files:
            latest_video = max(recorded_files, key=os.path.getctime)
            final_output = output_dir / "output-reel.webm"
            if final_output.exists():
                final_output.unlink()
            latest_video.rename(final_output)
            print(f"Terminal reel successfully rendered: {final_output}")

if __name__ == "__main__":
    print("Initializing Terminal Brutalist Autonomous Reel Engine...")
    hook_payload = generate_terminal_reel_hook()
    print("Terminal Hook Payload:", hook_payload)
    render_terminal_reel(hook_payload)
