import os
import sys
import textwrap
from pathlib import Path

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
    TextClip,
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


def _wrap_text_for_reels(text: str, max_chars_per_line: int = 24) -> str:
    """Wraps text into clean, human-readable lines that stay within horizontal bounds."""
    text = text.upper().strip()
    wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)
    return "\n".join(wrapped_lines)


def _process_micro_chunks(text: str, max_words_per_chunk: int = 10) -> list[str]:
    """Splits heavy text blocks into fast-paced micro-captions for high-retention editing."""
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
    font_path = resolve_font_path()

    active_theme = script_data.get("theme", theme)
    theme_config = COLOR_TOKENS.get(active_theme, COLOR_TOKENS.get("sovereign", COLOR_TOKENS[list(COLOR_TOKENS.keys())[0]]))

    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # Extract full voiceover script for 1:1 audio-visual sync
    raw_voiceover = script_data.get("voiceover_script", "").strip()
    if not raw_voiceover:
        raw_voiceover = f"{script_data.get('hook_text', '')} {' '.join(script_data.get('body_points', []))} {script_data.get('call_to_action', '')}".strip()
    if not raw_voiceover:
        raw_voiceover = script_data.get("title", "EXECUTE")

    # Generate micro-captions from the exact spoken script
    text_chunks = _process_micro_chunks(raw_voiceover, max_words_per_chunk=10)
    chunk_count = len(text_chunks)
    chunk_duration = total_duration / max(chunk_count, 1)

    visual_queries = script_data.get("visual_search_queries") or ["dark aesthetic"]
    scene_clips = []

    # Instagram Safe-Zone Dimensions (1080 x 1920 Canvas)
    MAX_TEXT_WIDTH = 840   # 120px safe margin left/right
    MAX_TEXT_HEIGHT = 800  # Allows up to 5-6 lines

    for chunk_idx, chunk in enumerate(text_chunks):
        # Rotate or map visual search query across chunks
        q_idx = min(int((chunk_idx / chunk_count) * len(visual_queries)), len(visual_queries) - 1)
        search_query = str(visual_queries[q_idx]).lower()

        bg_video_path = fetch_background_video(search_query, chunk_idx, chunk_duration)

        # 1. Background Layer Execution
        if bg_video_path and os.path.exists(bg_video_path):
            try:
                raw_bg = VideoFileClip(bg_video_path).without_audio()
                if raw_bg.duration < chunk_duration:
                    try:
                        raw_bg = raw_bg.loop(duration=chunk_duration)
                    except AttributeError:
                        # Fallback for MoviePy version differences
                        raw_bg = raw_bg.subclipped(0, min(raw_bg.duration, chunk_duration))
                else:
                    raw_bg = raw_bg.subclipped(0, chunk_duration)

                bg_clip = _crop_and_center_video(raw_bg, CANVAS_WIDTH, CANVAS_HEIGHT)
            except Exception as e:
                print(f"[!] Background crop/render error for chunk {chunk_idx+1}: {e}. Falling back to color clip.")
                bg_clip = ColorClip(
                    size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                    color=theme_config.get("bg", (15, 15, 18)),
                    duration=chunk_duration,
                )
        else:
            bg_clip = ColorClip(
                size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                color=theme_config.get("bg", (15, 15, 18)),
                duration=chunk_duration,
            )

        # Contrast mask overlay
        dark_overlay = ColorClip(
            size=(CANVAS_WIDTH, CANVAS_HEIGHT),
            color=(0, 0, 0),
            duration=chunk_duration,
        ).with_opacity(theme_config.get("mask_opacity", 0.55))

        # 2. Typography Assembly with Safe Line Wrapping
        formatted_text = _wrap_text_for_reels(chunk, max_chars_per_line=22)
        line_count = len(formatted_text.split("\n"))
        font_size = 52 if line_count <= 2 else (44 if line_count <= 4 else 36)

        text_subclips = []
        try:
            txt = TextClip(
                text=formatted_text,
                font_size=font_size,
                color=theme_config.get("text", "white"),
                font=font_path,
                stroke_color="black",
                stroke_width=3,
                method="caption",
                size=(MAX_TEXT_WIDTH, MAX_TEXT_HEIGHT),
            ).with_duration(chunk_duration).with_position(("center", "center"))
            
            text_subclips.append(txt)
        except Exception as e:
            print(f"[!] TextClip rendering error on chunk {chunk_idx+1}: {e}")

        chunk_composite = CompositeVideoClip([bg_clip, dark_overlay] + text_subclips).with_duration(chunk_duration)
        scene_clips.append(chunk_composite)

    if not scene_clips:
        fallback_bg = ColorClip(
            size=(CANVAS_WIDTH, CANVAS_HEIGHT),
            color=theme_config.get("bg", (15, 15, 18)),
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
    print(f"[+] [{active_theme.upper()}] Synchronized micro-caption Reel generated -> {target_output}")
    return target_output
