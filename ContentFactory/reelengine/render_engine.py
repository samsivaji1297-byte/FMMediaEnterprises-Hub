import os
import subprocess
from playwright.sync_api import sync_playwright

def render_html_to_mp4(html_path: str, final_mp4_path: str, duration_sec: float = 13.6):
    abs_html = f"file://{os.path.abspath(html_path)}"
    temp_dir = "ContentFactory/reelengine/tmp_video"
    os.makedirs(temp_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1080, "height": 1920},
            device_scale_factor=1,
            record_video_dir=temp_dir,
            record_video_size={"width": 1080, "height": 1920}
        )
        page = context.new_page()
        page.goto(abs_html, wait_until="networkidle")
        page.wait_for_timeout(int(duration_sec * 1000))
        
        video_path = page.video.path()
        context.close()
        browser.close()

    # Convert WebM capture to Instagram-compliant H.264 MP4 (1080x1920, yuv420p, 30fps)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-r", "30",
        final_mp4_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(video_path):
        os.remove(video_path)
    print(f"Rendered MP4: {final_mp4_path}")
