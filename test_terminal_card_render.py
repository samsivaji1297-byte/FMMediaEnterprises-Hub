import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip

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
    """Renders a sleek, proportional terminal UI card on a dark cinematic background."""
    # 1. Base Canvas (Dark Cinematic Background)
    img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), (12, 12, 16))
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_path = _resolve_font_path()
    try:
        font_badge = ImageFont.truetype(font_path, 22)
        font_main = ImageFont.truetype(font_path, 48)
    except Exception:
        font_badge = ImageFont.load_default()
        font_main = ImageFont.load_default()

    # 2. Compact Card Dimensions & Centering
    card_w = 900
    card_h = 480  # Compact, sleek height proportional to 2-3 lines of text
    card_x = (CANVAS_WIDTH - card_w) // 2
    card_y = (CANVAS_HEIGHT - card_h) // 2 + 100
    radius = 28

    accent_rgb = _hex_to_rgb(accent_hex)

    # Draw Frosted Obsidian Card Background
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        fill=(18, 18, 24),          # Deep dark obsidian fill
        outline=(45, 45, 60),       # Structural border edge
        width=2
    )

    # Draw Accent Glow Border Frame
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        outline=accent_rgb,
        width=2
    )

    # 3. Dynamic Top System Pill Badge
    badge_text = "■ SYSTEM DOSSIER // ACTIVE TRACE"
    
    # Calculate exact text width to wrap the pill perfectly
    try:
        badge_text_w = draw.textlength(badge_text, font=font_badge)
    except AttributeError:
        badge_text_w = len(badge_text) * 12  # Fallback approximation

    badge_w = int(badge_text_w) + 48
    badge_h = 40
    badge_x = card_x + 40
    badge_y = card_y + 35

    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=20,
        fill=(accent_rgb[0]//5, accent_rgb[1]//5, accent_rgb[2]//5),
        outline=accent_rgb,
        width=1
    )
    draw.text((badge_x + 24, badge_y + 9), badge_text, fill=accent_rgb, font=font_badge)

    # 4. Main Body Typography & Wrapping
    wrapped_lines = textwrap.wrap(text.upper(), width=23)
    text_y = badge_y + 65

    for line in wrapped_lines:
        draw.text((card_x + 40, text_y), line, fill=(255, 255, 255), font=font_main)
        text_y += 62

    os.makedirs("vault_test", exist_ok=True)
    out_path = "vault_test/solid_test_frame.png"
    img.save(out_path)
    return out_path

def build_test_video():
    print("[+] Initializing Proportional Terminal Card Test...")
    duration = 4.0

    sample_text = "MANUAL PROCESSES ARE OPERATIONAL LEAKS. DEPLOY AUTOMATED FLOWS."
    frame_path = generate_solid_frame(sample_text, accent_hex="#00E5FF")

    clip = ImageClip(frame_path).with_duration(duration)

    output_file = "test_output_reel.mp4"
    clip.write_videofile(
        output_file,
        fps=CANVAS_FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
    )
    print(f"[+] Proportional Test Reel Compiled Successfully -> {output_file}")

if __name__ == "__main__":
    build_test_video()
