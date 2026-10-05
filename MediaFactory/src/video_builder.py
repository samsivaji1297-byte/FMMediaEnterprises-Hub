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
        # Video is wider than 9:16 -> Crop sides
        new_w = int(orig_h * target_aspect)
        x_center = orig_w / 2
        x1 = int(x_center - (new_w / 2))
        cropped = clip.cropped(x1=x1, y1=0, width=new_w, height=orig_h)
    else:
        # Video is taller or already vertical -> Crop top/bottom
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


def _synthesize_scenes_from_script(script_data: dict) -> list:
    """Constructs scene structure if root dictionary fields are passed."""
    scenes = []

    hook_text = script_data.get("hook_text") or script_data.get("hook")
    if hook_text:
        scenes.append({
            "text_overlay": str(hook_text),
            "search_query": script_data.get("visual_search_queries", ["abstract dark"])[0] if script_data.get("visual_search_queries") else "abstract dark"
        })

    body_points = script_data.get("body_points") or script_data.get("body_bullets") or []
    visual_queries = script_data.get("visual_search_queries") or script_data.get("visual_keywords") or []

    for idx, point in enumerate(body_points):
        q = visual_queries[min(idx + 1, len(visual_queries) - 1)] if visual_queries else "focus execution"
        scenes.append({
            "text_overlay": str(point),
            "search_query": str(q)
        })

    cta_text = script_data.get("call_to_action") or script_data.get("cta")
    if cta_text:
        scenes.append({
            "text_overlay": str(cta_text),
            "search_query": "action execution"
        })

    if not scenes:
        scenes = [{"text_overlay": script_data.get("title", "EXECUTE"), "search_query": "dark aesthetic"}]

    return scenes


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

    scenes = script_data.get("scenes", [])
    if not scenes:
        scenes = _synthesize_scenes_from_script(script_data)

    scene_count = len(scenes)
    duration_per_scene = total_duration / max(scene_count, 1)

    scene_clips = []

    # Instagram Safe-Zone Dimensions (1080 x 1920 Canvas)
    MAX_TEXT_WIDTH = 840   # 120px safe margin left/right (prevents UI cutoff)
    MAX_TEXT_HEIGHT = 800  # Allows up to 5-6 lines of readable text

    for i, scene in enumerate(scenes):
        search_query = scene.get("search_query") or scene.get("text_overlay", "dark aesthetic")
        search_query = str(search_query).lower()

        bg_video_path = fetch_background_video(search_query, i, duration_per_scene)

        # 1. Background Layer Execution (NO MORE theme override bypassing B-roll!)
        if bg_video_path and os.path.exists(bg_video_path):
            try:
                raw_bg = VideoFileClip(bg_video_path).without_audio()
                if raw_bg.duration < duration_per_scene:
                    raw_bg = raw_bg.loop(duration=duration_per_scene)
                else:
                    raw_bg = raw_bg.subclipped(0, duration_per_scene)

                bg_clip = _crop_and_center_video(raw_bg, CANVAS_WIDTH, CANVAS_HEIGHT)
            except Exception as e:
                print(f"[!] Background crop/render error for scene {i+1}: {e}. Falling back to color clip.")
                bg_clip = ColorClip(
                    size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                    color=theme_config.get("bg", (15, 15, 18)),
                    duration=duration_per_scene,
                )
        else:
            bg_clip = ColorClip(
                size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                color=theme_config.get("bg", (15, 15, 18)),
                duration=duration_per_scene,
            )

        # Contrast mask overlay (Ensures text readability over video background)
        dark_overlay = ColorClip(
            size=(CANVAS_WIDTH, CANVAS_HEIGHT),
            color=(0, 0, 0),
            duration=duration_per_scene,
        ).with_opacity(theme_config.get("mask_opacity", 0.55))

        # 2. Typography Assembly with Safe Line Wrapping
        raw_text = scene.get("text_overlay", "").strip()
        formatted_text = _wrap_text_for_reels(raw_text, max_chars_per_line=22)

        # Dynamic Font Scaling based on length
        line_count = len(formatted_text.split("\n"))
        font_size = 48 if line_count <= 3 else (40 if line_count <= 5 else 34)

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
            ).with_duration(duration_per_scene).with_position(("center", "center"))
            
            text_subclips.append(txt)
        except Exception as e:
            print(f"[!] TextClip rendering error on scene {i+1}: {e}")

        scene_composite = CompositeVideoClip([bg_clip, dark_overlay] + text_subclips).with_duration(
            duration_per_scene
        )
        scene_clips.append(scene_composite)

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
    print(f"[+] [{active_theme.upper()}] Reel generated with B-Roll -> {target_output}")
    return target_output
