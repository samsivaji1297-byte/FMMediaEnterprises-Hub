import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from moviepy import (
    ColorClip,
    ImageClip,
    CompositeVideoClip,
    TextClip,
)

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

def generate_test_card(text: str, accent_hex: str = "#00E5FF") -> str:
    """Renders the frosted obsidian terminal UI card as a transparent PNG."""
    img = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    card_w = 940
    card_h = 700
    card_x = (CANVAS_WIDTH - card_w) // 2
    card_y = (CANVAS_HEIGHT - card_h) // 2 + 120
    radius = 36

    accent_rgb = _hex_to_rgb(accent_hex)

    # 1. Frosted Obsidian Glassmorphic Background
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        fill=(10, 10, 14, 240),      # Deep translucent dark fill
        outline=(40, 40, 55, 255),    # Structural edge
        width=3
    )

    # 2. Accent Glow Border
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        outline=(*accent_rgb, 200),
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
        fill=(*accent_rgb, 45),
        outline=(*accent_rgb, 220),
        width=1
    )
    draw.text((badge_x + 25, badge_y + 11), badge_text, fill=accent_rgb, font=font_badge)

    # 4. Main Body Typography
    wrapped_lines = textwrap.wrap(text.upper(), width=21)
    text_y = badge_y + 90

    for line in wrapped_lines:
        draw.text((card_x + 50, text_y), line, fill=(255, 255, 255, 255), font=font_main)
        text_y += 75

    os.makedirs("vault_test", exist_ok=True)
    out_path = "vault_test/test_card_frame.png"
    img.save(out_path)
    return out_path

def build_test_video():
    print("[+] Initializing Standalone Terminal Card Test...")
    duration = 4.0  # 4 second test clip
    
    # Mock background (Simulating a dark cinematic video surface)
    bg_clip = ColorClip(size=(CANVAS_WIDTH, CANVAS_HEIGHT), color=(20, 20, 25), duration=duration)
    
    # Dark contrast mask overlay
    mask_clip = ColorClip(size=(CANVAS_WIDTH, CANVAS_HEIGHT), color=(0, 0, 0), duration=duration).with_opacity(0.65)

    # Generate test PIL card graphic
    sample_text = "MANUAL PROCESSES ARE OPERATIONAL LEAKS. DEPLOY AUTOMATED FLOWS."
    card_img_path = generate_test_card(sample_text, accent_hex="#00E5FF")

    # CRITICAL: transparent=True and fromalpha=True ensures MoviePy respects the card's rounded alpha cutout
    card_clip = ImageClip(card_img_path, transparent=True, fromalpha=True).with_duration(duration)

    # Composite scene
    final_composite = CompositeVideoClip([bg_clip, mask_clip, card_clip]).with_duration(duration)

    output_file = "test_output_reel.mp4"
    final_composite.write_videofile(
        output_file,
        fps=CANVAS_FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
    )
    print(f"[+] Test Reel Compiled Successfully -> {output_file}")

if __name__ == "__main__":
    build_test_video()
