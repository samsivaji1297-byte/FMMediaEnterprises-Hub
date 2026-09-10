import os
from PIL import Image, ImageEnhance
from moviepy import (
    AudioFileClip, 
    VideoFileClip,
    ColorClip,
    TextClip, 
    CompositeVideoClip, 
    concatenate_videoclips
)
from video_fetcher import fetch_background_video

FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def build_video(script_data: dict, audio_path: str, theme: str = "ambient", output_path: str = "final_reel.mp4"):
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    scenes = script_data.get("scenes", [])
    scene_count = len(scenes)
    duration_per_scene = total_duration / max(scene_count, 1)
    
    scene_clips = []
    
    for i, scene in enumerate(scenes):
        search_query = scene.get("text_overlay", "city night lights").lower()
        bg_video_path = fetch_background_video(search_query, i, duration_per_scene)
        
        # 1. Background Layer (Motion Video vs Stark Color)
        if theme == "sovereign" or not bg_video_path or not os.path.exists(bg_video_path):
            bg_clip = ColorClip(size=(1080, 1920), color=(10, 10, 10), duration=duration_per_scene)
        else:
            try:
                # Load motion background clip and crop/resize to 1080x1920 vertical
                raw_bg = VideoFileClip(bg_video_path).without_audio()
                if raw_bg.duration < duration_per_scene:
                    raw_bg = raw_bg.loop(duration=duration_per_scene)
                else:
                    raw_bg = raw_bg.subclipped(0, duration_per_scene)
                    
                bg_clip = raw_bg.resized(new_size=(1080, 1920))
            except Exception as e:
                print(f"Error processing video background clip {i}: {e}. Falling back to black canvas.")
                bg_clip = ColorClip(size=(1080, 1920), color=(10, 10, 10), duration=duration_per_scene)

        # Dark overlay mask to ensure white/yellow captions pop against bright light trails
        dark_overlay = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration_per_scene).with_opacity(0.55)

        # 2. Typography & Kinetic Caption Layer
        raw_text = scene.get("text_overlay", "").upper().strip()
        words = raw_text.split() if raw_text else ["EXECUTE"]
        
        text_subclips = []
        
        if theme == "kinetic":
            word_duration = duration_per_scene / len(words)
            for w_idx, word in enumerate(words):
                txt = TextClip(
                    text=word,
                    font_size=100,
                    color='#FFE600',
                    font=FONT_PATH,
                    stroke_color='black',
                    stroke_width=6,
                    method='caption',
                    size=(900, None)
                ).with_duration(word_duration).with_position('center').with_start(w_idx * word_duration)
                text_subclips.append(txt)
        else:
            caption_text = "\n".join([" ".join(words[j:j+3]) for j in range(0, len(words), 3)])
            txt_color = '#FFFFFF' if theme == "sovereign" else '#F0F0F0'
            
            txt = TextClip(
                text=caption_text,
                font_size=85,
                color=txt_color,
                font=FONT_PATH,
                method='caption',
                size=(920, None)
            ).with_duration(duration_per_scene).with_position('center')
            text_subclips.append(txt)

        # Layer together: [Motion Video BG] + [Dark Overlay Mask] + [Kinetic Captions]
        scene_composite = CompositeVideoClip([bg_clip, dark_overlay] + text_subclips).with_duration(duration_per_scene)
        scene_clips.append(scene_composite)
        
    final_video = concatenate_videoclips(scene_clips, method="compose")
    final_video = final_video.with_audio(audio)
    
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4
    )
    print(f"[{theme.upper()}] Reel with motion background successfully generated -> {output_path}")
