import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920
CANVAS_FPS = 60
DURATION_SEC = 9.6  # Matches reference video length precisely

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
            background: #080a0f;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            overflow: hidden;
            position: relative;
        }

        /* Ambient Background Scrolling Manifestos */
        .ambient-bg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0.05;
            color: #ffffff;
            font-size: 32px;
            font-weight: 600;
            line-height: 2.2;
            padding: 80px;
            z-index: 1;
            user-select: none;
            pointer-events: none;
        }

        /* ACT 1: Full-Screen Macro Hook */
        .hook-scene {
            position: absolute;
            width: 900px;
            text-align: center;
            z-index: 20;
            animation: hookSequence 9.6s forwards;
        }

        .hook-title {
            font-size: 68px;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.25;
            letter-spacing: -0.5px;
        }

        .hook-title .highlight {
            background: linear-gradient(135deg, #70a1ff 0%, #00e5ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding: 0 4px;
        }

        .workbook-subtitle {
            font-size: 24px;
            color: #8b9bb4;
            margin-top: 20px;
            font-weight: 500;
            letter-spacing: 0.5px;
            opacity: 0.9;
        }

        @keyframes hookSequence {
            0% { opacity: 0; transform: translateY(-30px); }
            12% { opacity: 1; transform: translateY(0); }
            78% { opacity: 1; transform: translateY(0); }
            90% { opacity: 0; transform: translateY(-20px); }
            100% { opacity: 0; transform: translateY(-20px); }
        }

        /* ACT 2: Interactive Kill List UI Card */
        .kill-list-card {
            position: absolute;
            width: 920px;
            background: rgba(12, 16, 26, 0.95);
            backdrop-filter: blur(30px);
            border: 2px solid rgba(0, 229, 255, 0.3);
            border-radius: 32px;
            padding: 45px 50px;
            z-index: 15;
            box-shadow: 0 40px 80px rgba(0, 0, 0, 0.9),
                        0 0 50px rgba(0, 229, 255, 0.18);
            opacity: 0;
            transform: translateY(40px) scale(0.96);
            animation: cardSequence 9.6s forwards;
        }

        @keyframes cardSequence {
            0% { opacity: 0; transform: translateY(40px) scale(0.96); }
            18% { opacity: 0; transform: translateY(40px) scale(0.96); }
            24% { opacity: 1; transform: translateY(0) scale(1); }
            90% { opacity: 1; transform: translateY(0) scale(1); }
            100% { opacity: 0; transform: scale(0.98); }
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 24px;
            margin-bottom: 24px;
        }

        .card-title {
            font-size: 28px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 2px;
        }

        .counter-badge {
            font-size: 24px;
            font-weight: 700;
            color: #00e5ff;
            background: rgba(0, 229, 255, 0.12);
            padding: 6px 18px;
            border-radius: 14px;
            border: 1px solid rgba(0, 229, 255, 0.35);
        }

        .list-item {
            display: flex;
            align-items: center;
            padding: 16px 22px;
            margin-bottom: 12px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.04);
            color: #8b9bb4;
            font-size: 28px;
            font-weight: 600;
            transition: all 0.25s ease;
        }

        .item-num {
            font-family: monospace;
            color: #475569;
            margin-right: 20px;
            font-size: 24px;
        }

        /* Sequential Selection Triggers */
        .list-item.active-1 {
            background: rgba(0, 229, 255, 0.15) !important;
            border-color: #00e5ff !important;
            color: #ffffff !important;
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.3);
            transform: scale(1.01);
        }

        .list-item.active-2 {
            background: rgba(0, 229, 255, 0.15) !important;
            border-color: #00e5ff !important;
            color: #ffffff !important;
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.3);
            transform: scale(1.01);
        }

        .list-item.active-3 {
            background: rgba(0, 229, 255, 0.15) !important;
            border-color: #00e5ff !important;
            color: #ffffff !important;
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.3);
            transform: scale(1.01);
        }

        /* ACT 3: CTA Outro Footer */
        .cta-scene {
            position: absolute;
            bottom: 120px;
            width: 100%;
            text-align: center;
            opacity: 0;
            transform: translateY(20px);
            z-index: 20;
            animation: ctaSequence 9.6s forwards;
        }

        @keyframes ctaSequence {
            0% { opacity: 0; transform: translateY(20px); }
            75% { opacity: 0; transform: translateY(20px); }
            82% { opacity: 1; transform: translateY(0); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .cta-action {
            font-size: 34px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }

        .cta-sub {
            font-size: 24px;
            color: #00e5ff;
            font-weight: 700;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>

    <!-- Background Context -->
    <div class="ambient-bg">
        Be a new person overnight. Wake up at 4am.<br>
        Cold plunge. Journal. Run.<br>
        Read 50 books this year.<br>
        A perfect morning routine.<br>
        Change your whole life by Monday.<br>
        No excuses. No days off.
    </div>

    <!-- ACT 1: Hook Headline -->
    <div class="hook-scene">
        <div class="hook-title">
            Here's how you actually decide what to cut <span class="highlight">when rebuilding.</span>
        </div>
        <div class="workbook-subtitle">From the 90-Minute Protocol Workbook</div>
    </div>

    <!-- ACT 2: Interactive Card Engine -->
    <div class="kill-list-card">
        <div class="card-header">
            <div class="card-title">KILL LIST</div>
            <div class="counter-badge" id="counter">0 / 3</div>
        </div>

        <div class="list-item" id="i1"><span class="item-num">01</span> Doomscrolling at night</div>
        <div class="list-item" id="i2"><span class="item-num">02</span> Snoozing the alarm</div>
        <div class="list-item" id="i3"><span class="item-num">03</span> Saying yes to everything</div>
        <div class="list-item" id="i4"><span class="item-num">04</span> Comparing yourself online</div>
        <div class="list-item" id="i5"><span class="item-num">05</span> Skipping the plan</div>
        <div class="list-item" id="i6"><span class="item-num">06</span> Waiting to feel ready</div>
        <div class="list-item" id="i7"><span class="item-num">07</span> Half-finished projects</div>
        <div class="list-item" id="i8"><span class="item-num">08</span> Checking your phone first</div>
    </div>

    <!-- ACT 3: CTA Footer -->
    <div class="cta-scene">
        <div class="cta-action">Circle three of ten.</div>
        <div class="cta-sub">Comment KILL — I'll send you the workbook link.</div>
    </div>

    <script>
        // Precise beat synchronization timeline
        setTimeout(() => {
            document.getElementById('i3').classList.add('active-1');
            document.getElementById('counter').innerText = '1 / 3';
        }, 2800);

        setTimeout(() => {
            document.getElementById('i6').classList.add('active-2');
            document.getElementById('counter').innerText = '2 / 3';
        }, 4800);

        setTimeout(() => {
            document.getElementById('i8').classList.add('active-3');
            document.getElementById('counter').innerText = '3 / 3';
        }, 6800);
    </script>
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
    print("[+] Initializing Multi-Phase Cinematic Motion Engine...")
    html_path = generate_html_file()
    
    frames_dir = Path("vault_test/frames")
    frames_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": CANVAS_WIDTH, "height": CANVAS_HEIGHT})
        page.goto(f"file://{html_path}")
        
        total_frames = int(CANVAS_FPS * DURATION_SEC)
        frame_interval_ms = 1000 / CANVAS_FPS

        print(f"[+] Capturing {total_frames} multi-act frames at {CANVAS_FPS} FPS...")
        for frame in range(total_frames):
            frame_path = frames_dir / f"frame_{frame:04d}.png"
            page.screenshot(path=str(frame_path), type="png")
            page.wait_for_timeout(frame_interval_ms)

        browser.close()

    output_mp4 = "test_output_reel.mp4"
    print(f"[+] Compiling final multi-act MP4: {output_mp4}...")
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
    print(f"[+] Complete Multi-Act Reel Successfully Compiled -> {output_mp4}")

if __name__ == "__main__":
    render_motion_frames_to_video()
