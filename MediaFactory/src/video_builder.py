import os
import numpy as np
from PIL import Image, ImageEnhance
from moviepy import (
    AudioFileClip, 
    ImageClip, 
    ColorClip,
    TextClip, 
    CompositeVideoClip, 
    concatenate_videoclips
)

FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def apply_ken_burns(clip, zoom_ratio=0.08):
    """Adds a subtle continuous zoom effect to static images for dynamic movement."""
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        w, h = img.size
        # Calculate current scale factor based on clip time
        progress = t / clip.duration
        current_scale = 1.0 + (zoom_ratio * progress)
        
        # Crop and resize back to original vertical dimensions
        new_w, new_h = int(w / current_scale), int(h / current_scale)
        left = (w - new_w) // 2
        top = (h - new_h) // 2
        
        cropped = img.crop((left, top, left + new_w, top + new_h))
        resized = cropped.resize((w, h), Image.Resampling.LANCZOS)
        return np.array(resized)
        
    return clip.transform(effect)

def build_video(script_data: dict, audio_path: str, theme: str = "ambient", output_path: str = "final_reel.mp4"):
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    scenes = script_data.get("scenes", [])
    scene_count = len(scenes)
    duration_per_scene = total_duration / max(scene_count, 1)
    
    scene_clips = []
    
    for i, scene in enumerate(scenes):
        img_path = scene.get("image_path")
        
        # --- 1. BASE BACKGROUND LAYER ---
        if theme == "sovereign" or not img_path or not os.path.exists(img_path):
            # Pure Minimalist Stark Black Background
            bg_clip = ColorClip(size=(1080, 1920), color=(10, 10, 10), duration=duration_per_scene)
        else:
            # Dark Atmospheric AI Background with Dimming
            img = Image.open(img_path)
            # Darken image slightly so text pops
            enhancer = ImageEnhance.Brightness(img)
            darkened_img = enhancer.enhance(0.45)
            darkened_img_path = f"dark_{i}.jpg"
            darkened_img.save(darkened_img_path)
            
            base_bg = ImageClip(darkened_img_path).with_duration(duration_per_scene)
            bg_clip = apply_ken_burns(base_bg)

        # --- 2. TYPOGRAPHY & CAPTION LAYER ---
        raw_text = scene.get("text_overlay", "").upper().strip()
        words = raw_text.split() if raw_text else ["EXECUTE"]
        
        text_subclips = []
        
        if theme == "kinetic":
            # Word-by-Word Kinetic Pop Engine
            word_duration = duration_per_scene / len(words)
            for w_idx, word in enumerate(words):
                txt = TextClip(
                    text=word,
                    font_size=95,
                    color='#FFE600', # High visibility electric yellow
                    font=FONT_PATH,
                    stroke_color='black',
                    stroke_width=6,
                    method='caption',
                    size=(900, None)
                ).with_duration(word_duration).with_position('center').with_start(w_idx * word_duration)
                text_subclips.append(txt)
                
        else:
            # Sovereign & Ambient Style: Clean Centered Subtitles with High Signal Typography
            caption_text = "\n".join([" ".join(words[i:i+3]) for i in range(0, len(words), 3)])
            
            txt_color = '#FFFFFF' if theme == "sovereign" else '#F0F0F0'
            
            txt = TextClip(
                text=caption_text,
                font_size=80,
                color=txt_color,
                font=FONT_PATH,
                method='caption',
                size=(920, None)
            ).with_duration(duration_per_scene).with_position('center')
            
            text_subclips.append(txt)

        # Composite scene layers
        scene_composite = CompositeVideoClip([bg_clip] + text_subclips).with_duration(duration_per_scene)
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
    print(f"[{theme.upper()}] Reel successfully generated -> {output_path}")
