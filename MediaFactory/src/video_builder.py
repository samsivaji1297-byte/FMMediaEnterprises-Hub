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
    """Crops landscape or arbitrary footage into a clean 9:16 vertical stream before resizing."""
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
    return (0, 229, 255)  # Cyan default accent


def _generate_vignette_mask(canvas_w: int = CANVAS_WIDTH, canvas_h: int = CANVAS_HEIGHT) -> Image.Image:
    """
    Renders a solid RGBA gradient overlay (top/bottom dark vignette)
    to guarantee readability without obscuring full-screen motion footage.
    """
    mask = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)

    # Top dark gradient bar (for metadata badge readability)
    for y in range(0, 350):
        alpha = int(210 * (1 - (y / 350)))
        draw.line([(0, y), (canvas_w, y)], fill=(5, 8, 15, alpha))

    # Bottom dark gradient bar (for caption focus)
    for y in range(canvas_h - 600, canvas_h):
        progress = (y - (canvas_h - 600)) / 600
        alpha = int(230 * progress)
        draw.line([(0, y), (canvas_w, y)], fill=(5, 8, 15, alpha))

    return mask


def _generate_kinetic_text_overlay(
    chunk_text: str,
    theme_config: dict,
    font_path: str,
    scene_type: str = "HOOK",
    canvas_w: int = CANVAS_WIDTH,
    canvas_h: int = CANVAS_HEIGHT,
) -> str:
    """
    Renders a borderless RGBA kinetic typography overlay directly onto 
    full-screen motion video. Uses neon keyword pops, top pill HUDs, and clean shadows.
    """
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    
    # 1. Apply smooth dark vignette to base alpha layer
    vignette = _generate_vignette_mask(canvas_w, canvas_h)
    img.alpha_composite(vignette)

    draw = ImageDraw.Draw(img)
    accent_rgb = _hex_to_rgb(theme_config.get("accent", "#00E5FF"))

    # 2. Draw Top HUD / Metadata Pill (Non-intrusive top anchor)
    pill_text = f"■ SYSTEM // {scene_type}"
    try:
        font_pill = ImageFont.truetype(font_path, 26)
    except Exception:
        font_pill = ImageFont.load_default()

    pill_x = 80
    pill_y = 120
    pill_w = 420
    pill_h = 56

    draw.rounded_rectangle(
        [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
        radius=28,
        fill=(8, 12, 22, 200),
        outline=accent_rgb,
        width=2
    )
    draw.text((pill_x + 30, pill_y + 12), pill_text, fill=accent_rgb, font=font_pill)

    # 3. Render High-Impact Kinetic Typography (Centered 9:16 layout)
    try:
        font_main = ImageFont.truetype(font_path, 68)
    except Exception:
        font_main = ImageFont.load_default()

    cleaned_text = chunk_text.upper().strip()
    words = cleaned_text.split()
    wrapped_lines = textwrap.wrap(cleaned_text, width=14)

    # Center text vertically in the prime viewing zone
    total_text_height = len(wrapped_lines) * 92
    text_start_y = (canvas_h - total_text_height) // 2 + 100

    current_y = text_start_y
    for line in wrapped_lines:
        line_words = line.split()
        
        # Calculate line width for perfect center alignment
        total_line_w = sum(draw.textlength(w + " ", font=font_main) for w in line_words)
        start_x = (canvas_w - total_line_w) // 2

        curr_x = start_x
        for w in line_words:
            word_str = w + " "
            w_len = draw.textlength(word_str, font=font_main)

            # Highlight key action/power words in theme neon accent
            is_power_word = any(pw in w for pw in ["STOP", "RUNNING", "AUTOMATE", "MANUALLY", "OPERATIONS", "SYSTEMS", "SOVEREIGN", "DECK"])
            word_color = accent_rgb if is_power_word else (255, 255, 255)

            # Heavy drop shadow for instant legibility over active b-roll
            draw.text((curr_x + 4, current_y + 4), word_str, fill=(0, 0, 0, 240), font=font_main)
            draw.text((curr_x, current_y), word_str, fill=word_color + (255,), font=font_main)

            curr_x += w_len

        current_y += 92

    # Save temporary alpha overlay frame
    os.makedirs("MediaFactory/vault/temp", exist_ok=True)
    temp_img_path = f"MediaFactory/vault/temp/kinetic_{abs(hash(chunk_text))}.png"
    img.save(temp_img_path, "PNG")
    return temp_img_path


def _process_micro_chunks(text: str, max_words_per_chunk: int = 5) -> list[str]:
    """Splits full scripts into punchy, rapid-fire text cards for high retention."""
    words = text.split()
    if not words:
        return [text]
    chunks = []
    for i in range(0, len(words), max_words_per_chunk):
        chunks.append(" ".join(words[i:i + max_words_per_chunk]))
    return chunks if chunks else [text]


def build_video(
    script_data: dict,
    audio_path: str,
    theme: str = "sovereign",
    output_path: str = "final_reel.mp4",
):
    print("[+] Initializing Kinetic Motion Video Builder Engine...")
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

    text_chunks = _process_micro_chunks(raw_voiceover, max_words_per_chunk=5)
    chunk_count = len(text_chunks)
    chunk_duration = total_duration / max(chunk_count, 1)

    visual_queries = script_data.get("visual_search_queries") or ["dark abstract motion", "cyberpunk code terminal", "futuristic server room"]
    scene_clips = []
    temp_image_files = []

    for chunk_idx, chunk in enumerate(text_chunks):
        q_idx = min(int((chunk_idx / chunk_count) * len(visual_queries)), len(visual_queries) - 1)
        search_query = str(visual_queries[q_idx]).lower()

        # Fetch vertical motion b-roll clip
        bg_video_path = fetch_background_video(search_query, chunk_idx, chunk_duration)
        safe_bg_color = _hex_to_rgb(theme_config.get("bg", "#0A0F1D"))

        # Base Video Layer
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
                print(f"[!] Background video error for chunk {chunk_idx+1}: {e}. Falling back to dark canvas.")

        if bg_clip is None:
            bg_clip = ColorClip(
                size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                color=safe_bg_color,
                duration=chunk_duration,
            )

        # Scene Tagging for HUD
        if chunk_idx == 0:
            scene_type = "DISRUPTION HOOK"
        elif chunk_idx == chunk_count - 1:
            scene_type = "DIRECTIVE CTA"
        else:
            scene_type = f"CORE PROTOCOL 0{chunk_idx}"

        # Generate Transparent Kinetic Typography Overlay
        overlay_path = _generate_kinetic_text_overlay(chunk, theme_config, font_path, scene_type=scene_type)
        temp_image_files.append(overlay_path)

        overlay_clip = ImageClip(overlay_path).with_duration(chunk_duration)
        
        # Composite text directly OVER live full-screen video
        chunk_composite = CompositeVideoClip([bg_clip, overlay_clip]).with_duration(chunk_duration)
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

    # Cleanup temp frame overlays
    for img_path in temp_image_files:
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
        except Exception:
            pass

    print(f"[+] [{active_theme.upper()}] Kinetic Typography Reel successfully compiled -> {target_output}")
    return target_output
