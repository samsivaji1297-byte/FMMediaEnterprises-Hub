import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920
CANVAS_FPS = 60
DURATION_SEC = 9.0  # Matches the pacing of the reference reel

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
            justify-content: flex-start;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            overflow: hidden;
            position: relative;
            padding-top: 140px;
        }

        /* Ambient Background Scrolling Manifestos */
        .ambient-bg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0.04;
            color: #ffffff;
            font-size: 32px;
            font-weight: 600;
            line-height: 2.2;
            padding: 60px;
            z-index: 1;
            user-select: none;
            pointer-events: none;
        }

        /* Main Hook Section */
        .hook-container {
            width: 900px;
            text-align: center;
            z-index: 10;
            margin-bottom: 50px;
            animation: fadeInHook 0.6s ease-out forwards;
        }

        @keyframes fadeInHook {
            0% { opacity: 0; transform: translateY(-20px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .hook-title {
            font-size: 64px;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.25;
            letter-spacing: -0.5px;
            text-transform: none;
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
            margin-top: 16px;
            font-weight: 500;
            letter-spacing: 0.5px;
        }

        /* Interactive Checklist Card Container */
        .kill-list-card {
            width: 900px;
            background: rgba(14, 18, 28, 0.92);
            backdrop-filter: blur(25px);
            border: 2px solid rgba(0, 229, 255, 0.25);
            border-radius: 28px;
            padding: 40px 45px;
            z-index: 10;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.8),
                        0 0 40px rgba(0, 229, 255, 0.15);
            animation: slideUpCard 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.3s forwards;
            opacity: 0;
            transform: translateY(40px);
        }

        @keyframes slideUpCard {
            to { opacity: 1; transform: translateY(0); }
        }

        /* Card Header */
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
            background: rgba(0, 229, 255, 0.1);
            padding: 6px 16px;
            border-radius: 12px;
            border: 1px solid rgba(0, 229, 255, 0.3);
        }

        /* List Items */
        .list-item {
            display: flex;
            align-items: center;
            padding: 18px 24px;
            margin-bottom: 14px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.04);
            color: #94a3b8;
            font-size: 28px;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .item-num {
            font-family: monospace;
            color: #475569;
            margin-right: 20px;
            font-size: 24px;
        }

        /* Selection States triggered via CSS animations mapped to timeline */
        .list-item.sel-1 {
            animation: highlightItem 4s forwards;
            animation-delay: 2.5s;
        }

        .list-item.sel-2 {
            animation: highlightItem 4s forwards;
            animation-delay: 4.5s;
        }

        .list-item.sel-3 {
            animation: highlightItem 4s forwards;
            animation-delay: 6.5s;
        }

        @keyframes highlightItem {
            0% {
                background: rgba(255, 255, 255, 0.02);
                border-color: rgba(255, 255, 255, 0.04);
                color: #94a3b8;
            }
            15% {
                background: rgba(0, 229, 255, 0.12);
                border-color: #00e5ff;
                color: #ffffff;
                box-shadow: 0 0 25px rgba(0, 229, 255, 0.25);
                transform: scale(1.01);
            }
            100% {
                background: rgba(0, 229, 255, 0.08);
                border-color: rgba(0, 229, 255, 0.6);
                color: #ffffff;
                transform: scale(1);
            }
        }

        /* Dynamic Counter updates via CSS content simulation or script */
        
        /* CTA Footer Section */
        .cta-container {
            position: absolute;
            bottom: 100px;
            width: 100%;
            text-align: center;
            opacity: 0;
            animation: fadeInCTA 0.6s ease-out 7.5s forwards;
            z-index: 10;
        }

        @keyframes fadeInCTA {
            to { opacity: 1; transform: translateY(0); }
            from { opacity: 0; transform: translateY(20px); }
        }

        .cta-action {
            font-size: 32px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 8px;
        }

        .cta-sub {
            font-size: 22px;
            color: #00e5ff;
            font-weight: 600;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>

    <!-- Ambient background text context -->
    <div class="ambient-bg">
        Be a new person overnight. Wake up at 4am.<br>
        Cold plunge. Journal. Run.<br>
        Read 50 books this year.<br>
        A perfect morning routine.<br>
        Change your whole life by Monday.<br>
        No excuses. No days off.
    </div>

    <!-- Hook header -->
    <div class="hook-container">
        <div class="hook-title">
            Here's how you actually decide what to cut <span class="highlight">when rebuilding.</span>
        </div>
        <div class="workbook-subtitle">From the 90-Minute Protocol Workbook</div>
    </div>

    <!-- Kill List Card -->
    <div class="kill-list-card">
        <div class="card-header">
            <div class="card-title">KILL LIST</div>
            <div class="counter-badge" id="counter">0 / 3</div>
        </div>

        <div class="list-item" id="i1"><span class="item-num">01</span> Doomscrolling at night</div>
        <div class="list-item" id="i2"><span class="item-num">02</span> Snoozing the alarm</div>
        <div class="list-item sel-1" id="i3"><span class="item-num">03</span> Saying yes to everything</div>
        <div class="list-item" id="i4"><span class="item-num">04</span> Comparing yourself online</div>
        <div class="list-item" id="i5"><span class="item-num">05</span> Skipping the plan</div>
        <div class="list-item sel-2" id="i6"><span class="item-num">06</span> Waiting to feel ready</div>
        <div class="list-item" id="i7"><span class="item-num">07</span> Half-finished projects</div>
        <div class="list-item sel-3" id="i8"><span class="item-num">08</span> Checking your phone first</div>
    </div>

    <!-- CTA Footer -->
    <div class="cta-container">
        <div class="cta-action">Circle three of ten.</div>
        <div class="cta-sub">Comment KILL — I'll send you the workbook link.</div>
    </div>

    <script>
        // Simple DOM state hook to sync counter visual with highlighted items
        setTimeout(() => { document.getElementById('counter').innerText = '1 / 3'; }, 2700);
        setTimeout(() => { document.getElementById('counter').innerText = '2 / 3'; }, 4700);
        setTimeout(() => { document.getElementById('counter').innerText = '3 / 3'; }, 6700);
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
    print("[+] Initializing Viral-Aesthetic HTML Motion Engine...")
    html_path = generate_html_file()
    
    frames_dir = Path("vault_test/frames")
    frames_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": CANVAS_WIDTH, "height": CANVAS_HEIGHT})
        page.goto(f"file://{html_path}")
        
        total_frames = int(CANVAS_FPS * DURATION_SEC)
        frame_interval_ms = 1000 / CANVAS_FPS

        print(f"[+] Capturing {total_frames} cinematic frames at {CANVAS_FPS} FPS...")
        for frame in range(total_frames):
            frame_path = frames_dir / f"frame_{frame:04d}.png"
            page.screenshot(path=str(frame_path), type="png")
            page.wait_for_timeout(frame_interval_ms)

        browser.close()

    output_mp4 = "test_output_reel.mp4"
    print(f"[+] Compiling high-bitrate MP4: {output_mp4}...")
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
    print(f"[+] Viral Aesthetic Reel Successfully Compiled -> {output_mp4}")

if __name__ == "__main__":
    render_motion_frames_to_video()
