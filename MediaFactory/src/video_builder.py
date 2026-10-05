import os
import sys
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


def _synthesize_scenes_from_script(script_data: dict) -> list:
    """Fallback parser to construct scenes list if script_data provides root fields."""
    scenes = []

    # 1. Hook Scene
    hook_text = script_data.get("hook_text") or script_data.get("hook")
    if hook_text:
        scenes.append({
            "text_overlay": str(hook_text),
            "search_query": script_data.get("visual_search_queries", ["abstract dark"])[0] if script_data.get("visual_search_queries") else "abstract dark"
        })

    # 2. Body Points Scenes
    body_points = script_data.get("body_points") or script_data.get("body_bullets") or []
    visual_queries = script_data.get("visual_search_queries") or script_data.get("visual_keywords") or []
    
    for idx, point in enumerate(body_points):
        q = visual_queries[min(idx + 1, len(visual_queries) - 1)] if visual_queries else "focus execution"
        scenes.append({
            "text_overlay": str(point),
            "search_query": str(q)
        })

    # 3. Call To Action Scene
    cta_text = script_data.get("call_to_action") or script_data.get("cta")
    if cta_text:
        scenes.append({
            "text_overlay": str(cta_text),
            "search_query": "action execution"
        })

    # Fallback default if completely empty
    if not scenes:
        scenes = [
            {"text_overlay": script_data.get("title", "EXECUTE"), "search_query": "dark aesthetic"}
        ]

    return scenes


def build_video(
    script_data: dict,
    audio_path: str,
    theme: str = "sovereign",
    output_path: str = "final_reel.mp4",
):
    font_path = resolve_font_path()
    
    # Allow script_data to override default theme if specified
    active_theme = script_data.get("theme", theme)
    theme_config = COLOR_TOKENS.get(active_theme, COLOR_TOKENS.get("sovereign", COLOR_TOKENS[list(COLOR_TOKENS.keys())[0]]))

    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # Parse explicit scenes or synthesize from script_data attributes
    scenes = script_data.get("scenes", [])
    if not scenes:
        scenes = _synthesize_scenes_from_script(script_data)

    scene_count = len(scenes)
    duration_per_scene = total_duration / max(scene_count, 1)

    scene_clips = []

    for i, scene in enumerate(scenes):
        search_query = scene.get("search_query") or scene.get("text_overlay", "dark aesthetic")
        search_query = str(search_query).lower()
        
        bg_video_path = fetch_background_video(search_query, i, duration_per_scene)

        # 1. Background Layer Execution
        if active_theme == "sovereign" or not bg_video_path or not os.path.exists(bg_video_path):
            bg_clip = ColorClip(
                size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                color=theme_config["bg"],
                duration=duration_per_scene,
            )
        else:
            try:
                raw_bg = VideoFileClip(bg_video_path).without_audio()
                if raw_bg.duration < duration_per_scene:
                    raw_bg = raw_bg.loop(duration=duration_per_scene)
                else:
                    raw_bg = raw_bg.subclipped(0, duration_per_scene)

                bg_clip = raw_bg.resized(new_size=(CANVAS_WIDTH, CANVAS_HEIGHT))
            except Exception as e:
                print(f"[!] Video background render fallback for scene {i+1}: {e}")
                bg_clip = ColorClip(
                    size=(CANVAS_WIDTH, CANVAS_HEIGHT),
                    color=theme_config["bg"],
                    duration=duration_per_scene,
                )

        # Contrast overlay mask
        dark_overlay = ColorClip(
            size=(CANVAS_WIDTH, CANVAS_HEIGHT),
            color=(0, 0, 0),
            duration=duration_per_scene,
        ).with_opacity(theme_config.get("mask_opacity", 0.55))

        # 2. Kinetic / Static Caption Layer Assembly
        raw_text = scene.get("text_overlay", "").upper().strip()
        words = raw_text.split() if raw_text else ["EXECUTE"]
        text_subclips = []

        if active_theme == "kinetic":
            word_duration = duration_per_scene / max(len(words), 1)
            for w_idx, word in enumerate(words):
                try:
                    txt = TextClip(
                        text=word,
                        font_size=theme_config["font_size"],
                        color=theme_config["text"],
                        font=font_path,
                        stroke_color=theme_config.get("stroke", "black"),
                        stroke_width=5,
                        method="caption",
                        size=(900, None),
                    ).with_duration(word_duration).with_position("center").with_start(
                        w_idx * word_duration
                    )
                    text_subclips.append(txt)
                except Exception as e:
                    print(f"[!] TextClip rendering error on word '{word}': {e}")
        else:
            caption_text = "\n".join([" ".join(words[j : j + 3]) for j in range(0, len(words), 3)])
            try:
                txt = TextClip(
                    text=caption_text,
                    font_size=theme_config["font_size"],
                    color=theme_config["text"],
                    font=font_path,
                    method="caption",
                    size=(920, None),
                ).with_duration(duration_per_scene).with_position("center")
                text_subclips.append(txt)
            except Exception as e:
                print(f"[!] TextClip rendering error on scene {i+1}: {e}")

        scene_composite = CompositeVideoClip([bg_clip, dark_overlay] + text_subclips).with_duration(
            duration_per_scene
        )
        scene_clips.append(scene_composite)

    # Empty sequence safety guard
    if not scene_clips:
        print("[!] Warning: scene_clips is empty. Creating default fallback scene.")
        fallback_bg = ColorClip(
            size=(CANVAS_WIDTH, CANVAS_HEIGHT),
            color=theme_config["bg"],
            duration=total_duration,
        )
        scene_clips.append(fallback_bg)

    final_video = concatenate_videoclips(scene_clips, method="compose")
    final_video = final_video.with_audio(audio)

    # Resolve output directory target
    target_output = script_data.get("output_path", output_path)
    os.makedirs(os.path.dirname(os.path.abspath(target_output)), exist_ok=True)

    final_video.write_videofile(
        target_output,
        fps=CANVAS_FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None,  # Suppress verbose rendering logs
    )
    print(f"[+] [{active_theme.upper()}] Reel generated -> {target_output}")
    return target_output
