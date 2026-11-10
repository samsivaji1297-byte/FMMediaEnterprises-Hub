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
    """Renders a balanced dark vignette gradient to keep kinetic text razor-sharp over motion video."""
    mask = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)

    for y in range(canvas_h - 950, canvas_h):
        progress = (y - (canvas_h - 950)) / 950
        alpha = int(240 * progress)
        draw.line([(0, y), (canvas_w, y)], fill=(3, 5, 10, alpha))

    return mask


def _generate_kinetic_text_overlay(
    chunk_text: str,
    theme_config: dict,
    font_path: str,
    canvas_w: int = CANVAS_WIDTH,
    canvas_h: int = CANVAS_HEIGHT,
) -> str:
    """
    Renders pure, unobstructed kinetic typography directly onto 9:16 motion video.
    Zero amateur badges—only elite typography, neon highlights, and heavy drop shadows.
    """
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    
    vignette = _generate_vignette_mask(canvas_w, canvas_h)
    img.alpha_composite(vignette)

    draw = ImageDraw.Draw(img)
    accent_rgb = _hex_to_rgb(theme_config.get("accent", "#00E5FF"))

    try:
        font_main = ImageFont.truetype(font_path, 86)
    except Exception:
        font_main = ImageFont.load_default()

    cleaned_text = chunk_text.upper().strip()
    wrapped_lines = textwrap.wrap(cleaned_text, width=12)

    total_text_height = len(wrapped_lines) * 108
    text_start_y = (canvas_h - total_text_height) // 2 + 50

    current_y = text_start_y
    power_keywords = {
        "STOP", "RUNNING", "AUTOMATE", "MANUALLY", "OPERATIONS", "SYSTEMS", 
        "SOVEREIGN", "INFRASTRUCTURE", "LOSING", "HOURS", "KILL", "BOTTLENECK",
        "BUILD", "OPERATOR", "DECLARED", "CONVERT", "FREEDOM", "LEVERAGE", "TRADING"
    }

    for line in wrapped_lines:
        line_words = line.split()
        total_line_w = sum(draw.textlength(w + " ", font=font_main) for w in line_words)
        start_x = (canvas_w - total_line_w) // 2

        curr_x = start_x
        for w in line_words:
            word_str = w + " "
            w_len = draw.textlength(word_str, font=font_main)

            clean_w = "".join(c for c in w if c.isalnum())
            is_power_word = clean_w in power_keywords
            word_color = accent_rgb if is_power_word else (255, 255, 255)

            draw.text((curr_x + 6, current_y + 6), word_str, fill=(0, 0, 0, 255), font=font_main)
            draw.text((curr_x + 3, current_y + 3), word_str, fill=(0, 0, 0, 220), font=font_main)
            draw.text((curr_x, current_y), word_str, fill=word_color + (255,), font=font_main)

            curr_x += w_len

        current_y += 108

    os.makedirs("MediaFactory/vault/temp", exist_ok=True)
    temp_img_path = f"MediaFactory/vault/temp/kinetic_{abs(hash(chunk_text))}.png"
    img.save(temp_img_path, "PNG")
    return temp_img_path


def _process_micro_chunks(text: str, max_words_per_chunk: int = 4) -> list[str]:
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
    print("[+] Initializing Pure Kinetic Motion Engine...")
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

    text_chunks = _process_micro_chunks(raw_voiceover, max_words_per_chunk=4)
    chunk_count = len(text_chunks)
    chunk_duration = total_duration / max(chunk_count, 1)

    visual_queries = script_data.get("visual_search_queries") or ["dark abstract motion", "cyberpunk terminal", "glowing servers"]
    scene_clips = []
    temp_image_files = []

    for chunk_idx, chunk in enumerate(text_chunks):
        q_idx = min(int((chunk_idx / chunk_count) * len(visual_queries)), len(visual_queries) - 1)
        search_query = str(visual_queries[q_idx]).lower()

        bg_video_path = fetch_background_video(search_query, chunk_idx, chunk_duration)
        safe_bg_color = _hex_to_rgb(theme_config.get("bg", "#0A0F1D"))

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
                print(f"[!] B-roll loading issue for chunk {chunk_idx+1}: {e}. Deploying solid background.")

        if bg_clip is None:
            bg_clip = ColorClip(
                size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                color=safe_bg_color,
                duration=chunk_duration,
            )

        overlay_path = _generate_kinetic_text_overlay(chunk, theme_config, font_path)
        temp_image_files.append(overlay_path)

        overlay_clip = ImageClip(overlay_path).with_duration(chunk_duration)
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

    for img_path in temp_image_files:
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
        except Exception:
            pass

    print(f"[+] [{active_theme.upper()}] Pure Kinetic Typography Reel successfully compiled -> {target_output}")
    return target_output
