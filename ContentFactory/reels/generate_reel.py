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

def generate_kinetic_reel_content() -> dict:
    """Queries AI models for a multi-phase kinetic reel script designed for high-dopamine retention and conversion."""
    prompt = """
    You are an elite direct-response system architect crafting a multi-phase kinetic Instagram Reel script.
    
    Product & Framework Context:
    Digital operational frameworks (fmframeworks.gumroad.com), including 'The Compression System', 
    'Operator Mindset Kit', and the '90-Minute Protocol'.
    
    CORE COPYWRITING MANDATE:
    - Deliver absolute clarity, structural leverage, and mimetic dopamine hits. Make the viewer feel instantly productive and in control.
    - Provide a multi-phase narrative arc: Phase 1 (The Hook), Phase 2 (The Mechanism / Code Reveal), Phase 3 (The Sovereign Payoff).
    
    Return ONLY valid JSON matching this exact structure with no extra markdown or fluff:
    {
      "badge": "SYS.KERNEL // 02",
      "hookText": "HOW TO BUILD AN<br>AUTONOMOUS CONTENT<br>ENGINE IN 90 MINUTES",
      "mechanismText": "INJECTING config.py<br>+ PLAYWRIGHT PIPELINES<br>+ META GRAPH API",
      "payoffText": "DEPLOY ONCE.<br>RUN RECURSIVELY.<br>FMFRAMEWORKS.GUMROAD.COM"
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

def render_kinetic_reel(content: dict):
    """Renders a kinetic 1080x1920 multi-phase reel with synchronized Web Audio sound design via Playwright."""
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    template_path = Path(__file__).parent / 'template.html'

    embedded_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Kinetic Terminal IG Reel Studio</title>
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
    
    /* Kinetic Phases */
    .phase {{
      position: absolute; top: 320px; left: 90px; right: 90px; bottom: 320px;
      display: flex; flex-direction: column; justify-content: center;
      opacity: 0; transform: translateY(20px); transition: opacity 0.4s ease, transform 0.4s ease;
    }}
    .phase.active {{
      opacity: 1; transform: translateY(0);
    }}
    
    .phase-title {{
      font-family: 'Inter', sans-serif; font-weight: 800; font-size: 4.5rem;
      line-height: 1.12; text-transform: uppercase; color: #FFFFFF;
      letter-spacing: -0.02em; margin-bottom: 32px;
    }}
    .phase-title span {{ color: #FF6B00; }}
    
    .footer-block {{
      display: flex; justify-content: space-between; align-items: center;
      border-top: 1px solid rgba(255, 255, 255, 0.2); padding-top: 32px;
      width: 100%;
    }}
    .sub-text {{
      font-size: 1.15rem; font-weight: 500; letter-spacing: 0.2em;
      text-transform: uppercase; color: rgba(255, 255, 255, 0.7);
    }}
    .cta-link {{
      font-size: 1.1rem; letter-spacing: 0.25em; color: #FF6B00; font-weight: 700;
      text-transform: uppercase;
    }}
  </style>
</head>
<body>
  <div class="grid-overlay"></div>
  <div class="scanline"></div>
  
  <div class="content-container">
    <div class="header-block">
      <div class="badge" id="badge-text">{content['badge']}</div>
      <div class="timestamp">EXEC // SECURE</div>
    </div>
    
    <!-- Phase 1: Hook -->
    <div class="phase active" id="phase-1">
      <div class="phase-title">{content['hookText']}</div>
    </div>
    
    <!-- Phase 2: Mechanism / Explanation -->
    <div class="phase" id="phase-2">
      <div class="phase-title">{content['mechanismText']}</div>
    </div>
    
    <!-- Phase 3: Payoff / CTA -->
    <div class="phase" id="phase-3">
      <div class="phase-title">{content['payoffText']}</div>
    </div>
    
    <div class="footer-block">
      <div class="sub-text">SOVEREIGN PIPELINE</div>
      <div class="cta-link">→ FMFRAMEWORKS.GUMROAD.COM</div>
    </div>
  </div>

  <script>
    // Kinetic Phase Timeline & Web Audio Synthesizer
    window.addEventListener('DOMContentLoaded', () => {{
      try {{
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        const ctx = new AudioContext();
        
        // Background Sub-Bass Drone
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(55, ctx.currentTime);
        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 7.5);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 8.0);
        
        // UI Mechanical Ticks for Phase transitions
        function playTick() {{
          const t = ctx.currentTime;
          const cOsc = ctx.createOscillator();
          const cGain = ctx.createGain();
          cOsc.type = 'square';
          cOsc.frequency.setValueAtTime(1200, t);
          cGain.gain.setValueAtTime(0.04, t);
          cGain.gain.exponentialRampToValueAtTime(0.001, t + 0.04);
          cOsc.connect(cGain);
          cGain.connect(ctx.destination);
          cOsc.start(t);
          cOsc.stop(t + 0.04);
        }}
        
        // Timeline switching phases at 2.5s and 5.0s
        setTimeout(() => {{
          document.getElementById('phase-1').classList.remove('active');
          document.getElementById('phase-2').classList.add('active');
          document.getElementById('badge-text').innerText = 'SYS.KERNEL // 02.1';
          playTick();
        }}, 2500);
        
        setTimeout(() => {{
          document.getElementById('phase-2').classList.remove('active');
          document.getElementById('phase-3').classList.add('active');
          document.getElementById('badge-text').innerText = 'SYS.KERNEL // 03';
          playTick();
        }}, 5200);

      }} catch(e) {{
        console.log('Audio Context suppressed');
      }}
    }});
  </script>
</body>
</html>"""

    template_path.write_text(embedded_template, encoding='utf-8')

    print("Launching Playwright Kinetic recorder...")
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
        
        print("Recording 8-second multi-phase kinetic reel session...")
        time.sleep(8.0)
        
        context.close()
        browser.close()
        
        recorded_files = list(output_dir.glob("*.webm"))
        if recorded_files:
            latest_video = max(recorded_files, key=os.path.getctime)
            final_output = output_dir / "output-reel.webm"
            if final_output.exists():
                final_output.unlink()
            latest_video.rename(final_output)
            print(f"Kinetic reel successfully rendered: {final_output}")

if __name__ == "__main__":
    print("Initializing Kinetic Multi-Phase Autonomous Reel Engine...")
    content_payload = generate_kinetic_reel_content()
    print("Kinetic Payload:", content_payload)
    render_kinetic_reel(content_payload)
