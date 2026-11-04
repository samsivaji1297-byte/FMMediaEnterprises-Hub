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
    """Converts hex color string to RGB tuple."""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def _generate_ui_card_image(
    chunk_text: str,
    theme_config: dict,
    font_path: str,
    canvas_w: int = CANVAS_WIDTH,
    canvas_h: int = CANVAS_HEIGHT,
) -> str:
    """
    Renders a high-end UI Terminal Card onto a transparent canvas using PIL.
    """
    print(f"[✓] EXECUTING PIL UI CARD ENGINE FOR CHUNK: '{chunk_text[:30]}...'")
    
    # Create transparent base canvas
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Card dimensions & positioning (Centered in 9:16)
    card_w = 940
    card_h = 700
    card_x = (canvas_w - card_w) // 2
    card_y = (canvas_h - card_h) // 2 + 120
    radius = 36

    # Parse theme color tokens
    accent_hex = theme_config.get("accent", theme_config.get("text", "#00E5FF"))
    accent_rgb = _hex_to_rgb(accent_hex)

    # 1. Draw Frosted Glassmorphic Card Background (Dark Obsidian)
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        fill=(10, 10, 14, 235),       # Deep dark obsidian translucent fill
        outline=(40, 40, 55, 255),    # Structural inner edge
        width=3
    )

    # 2. Draw Accent Outer Glow Frame
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=radius,
        outline=(*accent_rgb, 180),   # Theme glow border
        width=2
    )

    # 3. Draw Top System Pill Badge
    badge_text = "■ SYSTEM DOSSIER // ACTIVE TRACE"
    try:
        font_badge = ImageFont.truetype(font_path, 24)
    except Exception:
        font_badge = ImageFont.load_default()

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
    draw.text(
        (badge_x + 25, badge_y + 11),
        badge_text,
        fill=accent_rgb,
        font=font_badge
    )

    # 4. Wrap and Render Main Caption Text
    try:
        font_main = ImageFont.truetype(font_path, 52)
    except Exception:
        font_main = ImageFont.load_default()

    cleaned_text = chunk_text.upper().strip()
    wrapped_lines = textwrap.wrap(cleaned_text, width=21)
    
    text_y = badge_y + 90

    for line in wrapped_lines:
        draw.text(
            (card_x + 50, text_y),
            line,
            fill=(255, 255, 255, 255),
            font=font_main
        )
        text_y += 75

    # 5. Save temporary frame asset
    os.makedirs("MediaFactory/vault/temp", exist_ok=True)
    temp_img_path = f"MediaFactory/vault/temp/card_{abs(hash(chunk_text))}.png"
    img.save(temp_img_path)
    return temp_img_path


def _process_micro_chunks(text: str, max_words_per_chunk: int = 7) -> list[str]:
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
    print("[+] Initializing Elevated PIL Video Builder Engine...")
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

    text_chunks = _process_micro_chunks(raw_voiceover, max_words_per_chunk=7)
    chunk_count = len(text_chunks)
    chunk_duration = total_duration / max(chunk_count, 1)

    visual_queries = script_data.get("visual_search_queries") or ["dark aesthetic"]
    scene_clips = []
    temp_image_files = []

    for chunk_idx, chunk in enumerate(text_chunks):
        q_idx = min(int((chunk_idx / chunk_count) * len(visual_queries)), len(visual_queries) - 1)
        search_query = str(visual_queries[q_idx]).lower()

        bg_video_path = fetch_background_video(search_query, chunk_idx, chunk_duration)

        # Background Layer
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
                print(f"[!] Background crop error for chunk {chunk_idx+1}: {e}. Fallback to color.")
                bg_clip = ColorClip(
                    size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                    color=theme_config.get("bg", (10, 10, 10)),
                    duration=chunk_duration,
                )
        else:
            bg_clip = ColorClip(
                size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                color=theme_config.get("bg", (10, 10, 10)),
                duration=chunk_duration,
            )

        # Contrast mask overlay
        dark_overlay = ColorClip(
            size=(CANVAS_WIDTH, CANVAS_HEIGHT),
            color=(0, 0, 0),
            duration=chunk_duration,
        ).with_opacity(theme_config.get("mask_opacity", 0.70))

        # Generate UI Card Graphic via PIL
        card_img_path = _generate_ui_card_image(chunk, theme_config, font_path)
        temp_image_files.append(card_img_path)

        card_clip = ImageClip(card_img_path, transparent=True, fromalpha=True).with_duration(chunk_duration)    
        
        chunk_composite = CompositeVideoClip([bg_clip, dark_overlay, card_clip]).with_duration(chunk_duration)
        scene_clips.append(chunk_composite)

    if not scene_clips:
        fallback_bg = ColorClip(
            size=(CANVAS_WIDTH, CANVAS_HEIGHT),
            color=theme_config.get("bg", (10, 10, 10)),
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

    print(f"[+] [{active_theme.upper()}] Terminal UI Card Reel successfully compiled -> {target_output}")
    return target_output
