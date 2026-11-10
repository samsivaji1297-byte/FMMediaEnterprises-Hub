import os
import sys
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Resolve internal imports regardless of entry point
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from design_tokens import (
    resolve_font_path,
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    CANVAS_FPS,
    COLOR_TOKENS,
)
from video_fetcher import fetch_background_video

from moviepy import (
    AudioFileClip,
    VideoFileClip,
    ColorClip,
    ImageClip,
    CompositeVideoClip,
    concatenate_videoclips,
)


def _crop_and_center_video(clip: VideoFileClip, target_w: int, target_h: int) -> VideoFileClip:
    """Crops a landscape or arbitrary clip to center 9:16 vertical before resizing."""
    orig_w, orig_h = clip.size
    target_aspect = target_w / target_h
    orig_aspect = orig_w / orig_h

    if orig_aspect > target_aspect:
        new_w = int(orig_h * target_aspect)
        x_center = orig_w / 2
        x1 = int(x_center - (new_w / 2))
        cropped = clip.cropped(x1=x1, y1=0, width=new_w, height=orig_h)
    else:
        new_h = int(orig_w / target_aspect)
        y_center = orig_h / 2
        y1 = int(y_center - (new_h / 2))
        cropped = clip.cropped(x1=0, y1=y1, width=orig_w, height=new_h)

    return cropped.resized(new_size=(target_w, target_h))


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Converts hex color string or tuple to clean RGB tuple."""
    if isinstance(hex_str, (list, tuple)):
        return tuple(int(c) for c in hex_str[:3])
    if isinstance(hex_str, str):
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 6:
            return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return (10, 15, 29)  # Fallback sovereign dark obsidian RGB


def _generate_ui_card_image(
    chunk_text: str,
    theme_config: dict,
    font_path: str,
    canvas_w: int = CANVAS_WIDTH,
    canvas_h: int = CANVAS_HEIGHT,
) -> str:
    """
    Renders a high-end UI Terminal Card onto a solid RGB background canvas 
    eliminating all transparency/alpha encoding bugs on Instagram.
    """
    print(f"[✓] EXECUTING ELITE PIL UI CARD ENGINE FOR CHUNK: '{chunk_text[:30]}...'")
    
    # Resolve background color safely as RGB tuple
    bg_hex = theme_config.get("bg", "#0A0F1D")
    bg_rgb = _hex_to_rgb(bg_hex)

    # Create solid RGB base canvas (Guarantees zero transparency encoding failures)
    img = Image.new("RGB", (canvas_w, canvas_h), bg_rgb)
    draw = ImageDraw.Draw(img)

    # Draw subtle ambient background grid / gradient lines for high-end aesthetic
    grid_color = (bg_rgb[0] + 15, bg_rgb[1] + 15, bg_rgb[2] + 20)
    for x_line in range(0, canvas_w, 80):
        draw.line([(x_line, 0), (x_line, canvas_h)], fill=grid_color, width=1)
    for y_line in range(0, canvas_h, 80):
        draw.line([(0, y_line), (canvas_w, y_line)], fill=grid_color, width=1)

    # Card dimensions & positioning (Centered in 9:16)
    card_w = 980
    card_h = 760
    card_x = (canvas_w - card_w) // 2
    card_y = (canvas_h - card_h) // 2 + 80
    radius = 32

    # Parse theme color tokens
    accent_hex = theme_config.get("accent", "#00E5FF")
    accent_rgb = _hex_to_rgb(accent_hex)

    # 1. Draw Frosted Glassmorphic Card Background (Deep Obsidian Opaque)
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        fill=(14, 18, 28),         # Solid rich dark slate fill (Zero alpha)
        outline=(50, 60, 80),      # Structural inner edge
        width=3
    )

    # 2. Draw Accent Outer Glow Frame
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        outline=accent_rgb,        # Theme neon border
        width=2
    )

    # 3. Draw Top System Pill Badge
    badge_text = "■ WAR ROOM INTEL // LIVE EXECUTION"
    try:
        font_badge = ImageFont.truetype(font_path, 22)
    except Exception:
        font_badge = ImageFont.load_default()

    badge_w = 460
    badge_h = 48
    badge_x = card_x + 60
    badge_y = card_y + 50

    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=24,
        fill=(accent_rgb[0]//4, accent_rgb[1]//4, accent_rgb[2]//4),
        outline=accent_rgb,
        width=1
    )
    draw.text(
        (badge_x + 25, badge_y + 12),
        badge_text,
        fill=accent_rgb,
        font=font_badge
    )

    # 4. Wrap and Render Main Caption Text with High Legibility
    try:
        font_main = ImageFont.truetype(font_path, 50)
    except Exception:
        font_main = ImageFont.load_default()

    cleaned_text = chunk_text.upper().strip()
    wrapped_lines = textwrap.wrap(cleaned_text, width=20)
    
    text_y = badge_y + 90

    for line in wrapped_lines:
        # Subtle drop shadow for crisp readability over any background
        draw.text((card_x + 62, text_y + 2), line, fill=(0, 0, 0), font=font_main)
        draw.text((card_x + 60, text_y), line, fill=(255, 255, 255), font=font_main)
        text_y += 72

    # 5. Save temporary frame asset
    os.makedirs("MediaFactory/vault/temp", exist_ok=True)
    temp_img_path = f"MediaFactory/vault/temp/card_{abs(hash(chunk_text))}.png"
    img.save(temp_img_path, "PNG")
    return temp_img_path


def _process_micro_chunks(text: str, max_words_per_chunk: int = 6) -> list[str]:
    """Splits heavy text blocks into fast-paced micro-captions."""
    words = text.split()
    if not words:
        return [text]
    chunks = []
    for i in range(0, len(words), max_words_per_chunk):
        chunk = " ".join(words[i:i + max_words_per_chunk])
        chunks.append(chunk)
    return chunks if chunks else [text]


def build_video(
    script_data: dict,
    audio_path: str,
    theme: str = "sovereign",
    output_path: str = "final_reel.mp4",
):
    print("[+] Initializing Elite Solid-State Video Builder Engine...")
    font_path = resolve_font_path()

    active_theme = script_data.get("theme", theme)
    theme_config = COLOR_TOKENS.get(active_theme, COLOR_TOKENS.get("sovereign", COLOR_TOKENS[list(COLOR_TOKENS.keys())[0]]))

    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    raw_voiceover = script_data.get("voiceover_script", "").strip()
    if not raw_voiceover:
        raw_voiceover = f"{script_data.get('hook_text', '')} {' '.join(script_data.get('body_points', []))} {script_data.get('call_to_action', '')}".strip()
    if not raw_voiceover:
        raw_voiceover = script_data.get("title", "EXECUTE")

    text_chunks = _process_micro_chunks(raw_voiceover, max_words_per_chunk=6)
    chunk_count = len(text_chunks)
    chunk_duration = total_duration / max(chunk_count, 1)

    visual_queries = script_data.get("visual_search_queries") or ["dark aesthetic"]
    scene_clips = []
    temp_image_files = []

    for chunk_idx, chunk in enumerate(text_chunks):
        q_idx = min(int((chunk_idx / chunk_count) * len(visual_queries)), len(visual_queries) - 1)
        search_query = str(visual_queries[q_idx]).lower()

        bg_video_path = fetch_background_video(search_query, chunk_idx, chunk_duration)
        safe_bg_color = _hex_to_rgb(theme_config.get("bg", "#0A0F1D"))

        # Background Layer with Bulletproof Fallback
        bg_clip = None
        if bg_video_path and os.path.exists(bg_video_path):
            try:
                raw_bg = VideoFileClip(bg_video_path).without_audio()
                if raw_bg.duration < chunk_duration:
                    try:
                        raw_bg = raw_bg.loop(duration=chunk_duration)
                    except AttributeError:
                        raw_bg = raw_bg.subclipped(0, min(raw_bg.duration, chunk_duration))
                else:
                    raw_bg = raw_bg.subclipped(0, chunk_duration)

                bg_clip = _crop_and_center_video(raw_bg, CANVAS_WIDTH, CANVAS_HEIGHT)
            except Exception as e:
                print(f"[!] Background video error for chunk {chunk_idx+1}: {e}. Falling back to solid color.")

        if bg_clip is None:
            bg_clip = ColorClip(
                size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                color=safe_bg_color,
                duration=chunk_duration,
            )

        # Contrast mask overlay (Safely applied without transparency glitches)
        dark_overlay = ColorClip(
            size=(CANVAS_WIDTH, CANVAS_HEIGHT),
            color=(0, 0, 0),
            duration=chunk_duration,
        ).with_opacity(float(theme_config.get("mask_opacity", 0.65)))

        # Generate pre-composited Solid UI Card Graphic via PIL
        card_img_path = _generate_ui_card_image(chunk, theme_config, font_path)
        temp_image_files.append(card_img_path)

        # Load as a pure RGB ImageClip (No alpha channel vulnerability)
        card_clip = ImageClip(card_img_path).with_duration(chunk_duration)
        
        # Composite chunk
        chunk_composite = CompositeVideoClip([bg_clip, dark_overlay, card_clip]).with_duration(chunk_duration)
        scene_clips.append(chunk_composite)

    if not scene_clips:
        fallback_bg = ColorClip(
            size=(CANVAS_WIDTH, CANVAS_HEIGHT),
            color=_hex_to_rgb(theme_config.get("bg", "#0A0F1D")),
            duration=total_duration,
        )
        scene_clips.append(fallback_bg)

    final_video = concatenate_videoclips(scene_clips, method="compose")
    final_video = final_video.with_audio(audio)

    target_output = script_data.get("output_path", output_path)
    os.makedirs(os.path.dirname(os.path.abspath(target_output)), exist_ok=True)

    final_video.write_videofile(
        target_output,
        fps=CANVAS_FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None,
    )

    # Cleanup temp card images
    for img_path in temp_image_files:
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
        except Exception:
            pass

    print(f"[+] [{active_theme.upper()}] Bulletproof Terminal UI Card Reel successfully compiled -> {target_output}")
    return target_output
