import os
import sys
import asyncio
from playwright.async_api import async_playwright

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Operator Mindset - Terminal Reel</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&family=Inter:wght@400;600;900&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            width: 1080px;
            height: 1920px;
            background: #09090b;
            color: #f4f4f5;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            position: relative;
        }

        /* Ambient Glow & Vignette */
        .ambient-glow {
            position: absolute;
            top: -200px;
            left: 50%;
            transform: translateX(-50%);
            width: 900px;
            height: 900px;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, rgba(9, 9, 11, 0) 70%);
            z-index: 1;
            pointer-events: none;
        }

        .vignette {
            position: absolute;
            inset: 0;
            background: radial-gradient(circle, transparent 50%, rgba(0,0,0,0.85) 100%);
            z-index: 10;
            pointer-events: none;
        }

        /* Canvas Container */
        .stage {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 80px;
            z-index: 5;
        }

        /* Terminal Window */
        .terminal-window {
            width: 920px;
            background: rgba(18, 18, 23, 0.85);
            border: 1px solid rgba(52, 211, 153, 0.3);
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 40px rgba(16, 185, 129, 0.1);
            overflow: hidden;
            backdrop-filter: blur(20px);
        }

        .terminal-header {
            background: rgba(24, 24, 27, 0.9);
            padding: 20px 24px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .dots {
            display: flex;
            gap: 8px;
        }

        .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        .dot-red { background: #ef4444; }
        .dot-yellow { background: #f59e0b; }
        .dot-green { background: #10b981; }

        .terminal-title {
            margin-left: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: #a1a1aa;
            letter-spacing: 0.05em;
        }

        .terminal-body {
            padding: 40px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 26px;
            line-height: 1.6;
            color: #e4e4e7;
        }

        /* Hook Chip */
        .hook-chip {
            display: inline-block;
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            padding: 8px 18px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 30px;
            border: 1px solid rgba(52, 211, 153, 0.3);
        }

        /* Staggered Rows */
        .code-row {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.4s ease, transform 0.4s ease;
            margin-bottom: 16px;
            display: flex;
            align-items: flex-start;
            gap: 16px;
        }

        .prompt {
            color: #10b981;
            font-weight: 800;
        }

        .highlight {
            color: #34d399;
            font-weight: 700;
        }

        .dim {
            color: #71717a;
        }

        /* Footer Brand */
        .brand-footer {
            margin-top: 50px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 18px;
            color: #71717a;
            letter-spacing: 0.15em;
            text-transform: uppercase;
        }
    </style>
</head>
<body>
    <div class="ambient-glow"></div>
    <div class="vignette"></div>

    <div class="stage">
        <div class="hook-chip" id="hookChip">OPERATOR PROTOCOL // v2.4</div>
        
        <div class="terminal-window">
            <div class="terminal-header">
                <div class="dots">
                    <div class="dot dot-red"></div>
                    <div class="dot dot-yellow"></div>
                    <div class="dot dot-green"></div>
                </div>
                <div class="terminal-title">matrix_compiler.py — secure_override</div>
            </div>
            <div class="terminal-body" id="termBody">
                <div class="code-row" id="row0"><span class="prompt">></span> <span>Initializing system sovereign core...</span></div>
                <div class="code-row" id="row1"><span class="prompt">></span> <span class="dim">Bypassing external API dependencies</span></div>
                <div class="code-row" id="row2"><span class="prompt">></span> <span class="highlight">Executing zero-latency data pipeline.</span></div>
                <div class="code-row" id="row3"><span class="prompt">></span> <span>Status: <span class="highlight">AUTONOMY ACHIEVED.</span></span></div>
            </div>
        </div>

        <div class="brand-footer" id="brandFooter">THE FINAL MINDSET</div>
    </div>

    <script>
        // Deterministic Frame Animation Engine driven by time parameter t (seconds)
        function setT(t) {
            // Duration: 5 seconds total
            const duration = 5.0;
            const progress = Math.min(Math.max(t / duration, 0), 1);

            // Hook Chip Animation (0.0s - 0.8s)
            const chip = document.getElementById('hookChip');
            const chipProgress = Math.min(Math.max(t / 0.8, 0), 1);
            chip.style.opacity = chipProgress;
            chip.style.transform = `translateY(${(1 - chipProgress) * -20}px) scale(${0.95 + chipProgress * 0.05})`;

            // Staggered Code Rows Animation (1.0s - 3.5s)
            const rows = [
                { id: 'row0', start: 1.0, end: 1.6 },
                { id: 'row1', start: 1.5, end: 2.1 },
                { id: 'row2', start: 2.0, end: 2.6 },
                { id: 'row3', start: 2.5, end: 3.1 }
            ];

            rows.forEach(r => {
                const el = document.getElementById(r.id);
                if (t >= r.start) {
                    const p = Math.min((t - r.start) / (r.end - r.start), 1);
                    // Ease out quad
                    const ease = p * (2 - p);
                    el.style.opacity = ease;
                    el.style.transform = `translateY(${(1 - ease) * 15}px)`;
                } else {
                    el.style.opacity = 0;
                    el.style.transform = `translateY(15px)`;
                }
            });

            // Footer Brand Fade In (3.5s - 4.5s)
            const footer = document.getElementById('brandFooter');
            const footerProgress = Math.min(Math.max((t - 3.5) / 1.0, 0), 1);
            footer.style.opacity = footerProgress;
        }

        // Expose setT globally for Playwright evaluation
        window.setT = setT;
    </script>
</body>
</html>
"""

async def render_reels():
    print("Initializing Playwright headless render engine...")
    html_path = "index_preview.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)

    fps = 30
    duration = 5.0
    total_frames = int(fps * duration)
    output_video = "operator_mindset_reel.mp4"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1080, "height": 1920},
            device_scale_factor=1
        )
        page = await context.new_page()
        
        # Load local HTML file
        abs_path = os.path.abspath(html_path)
        await page.goto(f"file://{abs_path}?export=1")
        await page.wait_for_load_state("networkidle")

        print(f"Rendering {total_frames} frames at {fps} fps...")

        # Setup ffmpeg process to pipe raw frames
        import subprocess
        cmd = [
            "ffmpeg", "-y",
            "-f", "image2pipe",
            "-r", str(fps),
            "-vcodec", "png",
            "-i", "-",
            "-vcodec", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            output_video
        ]
        
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for frame_idx in range(total_frames):
            t = frame_idx / fps
            # Evaluate deterministic time step in browser
            await page.evaluate(f"setT({t})")
            
            # Capture screenshot buffer
            screenshot_bytes = await page.screenshot(type="png", full_page=False)
            process.stdin.write(screenshot_bytes)
            
            if frame_idx % 30 == 0:
                print(f"Rendered frame {frame_idx}/{total_frames} (t={t:.2f}s)")

        process.stdin.close()
        process.wait()
        await browser.close()

    if os.path.exists(html_path):
        os.remove(html_path)

    print(f"Successfully rendered reel to {output_video}")

if __name__ == "__main__":
    asyncio.run(render_reels())
