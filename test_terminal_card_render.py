import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips

# Canvas Specs (9:16 Reels / Shorts)
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920
CANVAS_FPS = 30

def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Converts hex color string to RGB tuple."""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def _resolve_font_path() -> str:
    """Finds a reliable system font."""
    candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "DejaVuSans-Bold"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "DejaVuSans-Bold"

def generate_solid_frame(text: str, accent_hex: str = "#00E5FF") -> str:
    """Bakes the dark background, cinematic overlay, obsidian card, and text into a single solid frame."""
    # Create solid RGB base canvas (Dark Cinematic Background)
    img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), (15, 15, 20))
    draw = ImageDraw.Draw(img)

    # Draw subtle ambient background gradient or vignette lines if desired
    # (Solid dark base ensures zero black-screen risk)

    card_w = 940
    card_h = 700
    card_x = (CANVAS_WIDTH - card_w) // 2
    card_y = (CANVAS_HEIGHT - card_h) // 2 + 120
    radius = 36

    accent_rgb = _hex_to_rgb(accent_hex)

    # 1. Frosted Obsidian Glassmorphic Card Background (Solid opaque dark fill)
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        fill=(22, 22, 30),          # Solid dark obsidian box
        outline=(50, 50, 70),       # Structural inner edge
        width=3
    )

    # 2. Accent Glow Border
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        outline=accent_rgb,
        width=2
    )

    # 3. Top System Pill Badge
    font_path = _resolve_font_path()
    try:
        font_badge = ImageFont.truetype(font_path, 24)
        font_main = ImageFont.truetype(font_path, 52)
    except Exception:
        font_badge = ImageFont.load_default()
        font_main = ImageFont.load_default()

    badge_text = "■ SYSTEM DOSSIER // ACTIVE TRACE"
    badge_w = 420
    badge_h = 48
    badge_x = card_x + 50
    badge_y = card_y + 45

    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=24,
        fill=(accent_rgb[0]//4, accent_rgb[1]//4, accent_rgb[2]//4),
        outline=accent_rgb,
        width=1
    )
    draw.text((badge_x + 25, badge_y + 11), badge_text, fill=accent_rgb, font=font_badge)

    # 4. Main Body Typography
    wrapped_lines = textwrap.wrap(text.upper(), width=21)
    text_y = badge_y + 90

    for line in wrapped_lines:
        draw.text((card_x + 50, text_y), line, fill=(255, 255, 255), font=font_main)
        text_y += 75

    os.makedirs("vault_test", exist_ok=True)
    out_path = "vault_test/solid_test_frame.png"
    img.save(out_path)
    return out_path

def build_test_video():
    print("[+] Initializing Solid-Frame Terminal Card Test...")
    duration = 4.0  # 4 second test clip

    sample_text = "MANUAL PROCESSES ARE OPERATIONAL LEAKS. DEPLOY AUTOMATED FLOWS."
    frame_path = generate_solid_frame(sample_text, accent_hex="#00E5FF")

    # Load as a direct static image clip (no complex masks needed)
    clip = ImageClip(frame_path).with_duration(duration)

    output_file = "test_output_reel.mp4"
    clip.write_videofile(
        output_file,
        fps=CANVAS_FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
    )
    print(f"[+] Solid-Frame Test Reel Compiled Successfully -> {output_file}")

if __name__ == "__main__":
    build_test_video()
