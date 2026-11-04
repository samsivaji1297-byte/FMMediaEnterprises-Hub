import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920
CANVAS_FPS = 60
DURATION_SEC = 4.0

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            width: 1080px;
            height: 1920px;
            background: #08080c;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Liberation Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            overflow: hidden;
            position: relative;
        }

        /* Ambient Glow Background Pulse */
        .ambient-glow {
            position: absolute;
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(0, 229, 255, 0.15) 0%, rgba(0,0,0,0) 70%);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            animation: pulseGlow 4s ease-in-out infinite alternate;
        }

        @keyframes pulseGlow {
            0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.5; }
            100% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.9; }
        }

        /* Terminal Glassmorphic Container with Animated Border */
        .terminal-card {
            width: 880px;
            padding: 48px;
            background: rgba(14, 16, 22, 0.85);
            backdrop-filter: blur(20px);
            border-radius: 28px;
            position: relative;
            z-index: 10;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.8),
                        0 0 40px rgba(0, 229, 255, 0.2);
            border: 2px solid rgba(0, 229, 255, 0.4);
            animation: cardSlideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards,
                       borderGlow 3s ease-in-out infinite alternate;
        }

        @keyframes cardSlideUp {
            0% { opacity: 0; transform: translateY(60px) scale(0.95); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }

        @keyframes borderGlow {
            0% { border-color: rgba(0, 229, 255, 0.3); box-shadow: 0 0 20px rgba(0, 229, 255, 0.1); }
            100% { border-color: rgba(0, 229, 255, 0.8); box-shadow: 0 0 50px rgba(0, 229, 255, 0.35); }
        }

        /* Pill Badge */
        .pill-badge {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 10px 22px;
            background: rgba(0, 229, 255, 0.12);
            border: 1px solid rgba(0, 229, 255, 0.6);
            border-radius: 100px;
            color: #00E5FF;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 32px;
            text-transform: uppercase;
        }

        .pill-indicator {
            width: 10px;
            height: 10px;
            background: #00E5FF;
            border-radius: 50%;
            box-shadow: 0 0 10px #00E5FF;
            animation: blink 1.2s infinite alternate;
        }

        @keyframes blink {
            0% { opacity: 0.3; }
            100% { opacity: 1; }
        }

        /* Main Headline Typography */
        .headline {
            color: #FFFFFF;
            font-size: 46px;
            font-weight: 800;
            line-height: 1.35;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .highlight {
            color: #00E5FF;
            text-shadow: 0 0 15px rgba(0, 229, 255, 0.5);
        }

        /* Cursor Caret for Typewriter Effect */
        .cursor {
            display: inline-block;
            width: 12px;
            height: 44px;
            background: #00E5FF;
            margin-left: 6px;
            vertical-align: middle;
            animation: caretBlink 0.8s infinite;
        }

        @keyframes caretBlink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="ambient-glow"></div>
    <div class="terminal-card">
        <div class="pill-badge">
            <span class="pill-indicator"></span>
            SYSTEM DOSSIER // ACTIVE TRACE
        </div>
        <div class="headline">
            MANUAL PROCESSES ARE <span class="highlight">OPERATIONAL LEAKS</span>. DEPLOY AUTOMATED FLOWS.<span class="cursor"></span>
        </div>
    </div>
</body>
</html>
"""

def generate_html_file():
    os.makedirs("vault_test", exist_ok=True)
    html_path = Path("vault_test/card_template.html").resolve()
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)
    return html_path

def render_motion_frames_to_video():
    print("[+] Initializing HTML/CSS Motion Engine via Playwright...")
    html_path = generate_html_file()
    
    frames_dir = Path("vault_test/frames")
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Capture HTML animation frames in a headless browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": CANVAS_WIDTH, "height": CANVAS_HEIGHT})
        page.goto(f"file://{html_path}")
        
        total_frames = int(CANVAS_FPS * DURATION_SEC)
        frame_interval_ms = 1000 / CANVAS_FPS

        print(f"[+] Capturing {total_frames} motion frames at 60 FPS...")
        for frame in range(total_frames):
            frame_path = frames_dir / f"frame_{frame:04d}.png"
            page.screenshot(path=str(frame_path), type="png")
            page.wait_for_timeout(frame_interval_ms)

        browser.close()

    # Compile captured frames into 60 FPS MP4 via FFmpeg
    output_mp4 = "test_output_reel.mp4"
    print(f"[+] Compiling frame sequence into high-bitrate MP4: {output_mp4}...")
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-r", str(CANVAS_FPS),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        output_mp4
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"[+] Motion Graphic Reel Successfully Compiled -> {output_mp4}")

if __name__ == "__main__":
    render_motion_frames_to_video()
