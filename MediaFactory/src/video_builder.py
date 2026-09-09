import os
from moviepy import (
    AudioFileClip, 
    ImageClip, 
    TextClip, 
    CompositeVideoClip, 
    concatenate_videoclips
)

def build_video(script_data: dict, audio_path: str, output_path: str = "final_reel.mp4"):
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    scenes = script_data.get("scenes", [])
    scene_count = len(scenes)
    duration_per_scene = total_duration / max(scene_count, 1)
    
    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    scene_clips = []
    
    for i, scene in enumerate(scenes):
        img_path = scene.get("image_path")
        
        # 1. Base Image Clip with duration
        if img_path and os.path.exists(img_path):
            bg_clip = ImageClip(img_path).with_duration(duration_per_scene)
        else:
            # Fallback black screen if image failed
            from moviepy import ColorClip
            bg_clip = ColorClip(size=(1080, 1920), color=(15, 15, 15), duration=duration_per_scene)
        
        # 2. Dynamic Word-by-Word Kinetic Captions
        words = scene.get("text_overlay", "").upper().split()
        if not words:
            words = ["EXECUTE"]
            
        word_duration = duration_per_scene / len(words)
        text_subclips = []
        
        for w_idx, word in enumerate(words):
            # Dynamic text pop-in effect
            txt = TextClip(
                text=word,
                font_size=90,
                color='yellow',
                font=font_path,
                stroke_color='black',
                stroke_width=4,
                method='caption',
                size=(950, None)
            ).with_duration(word_duration).with_position('center').with_start(w_idx * word_duration)
            
            text_subclips.append(txt)
            
        # Composite dynamic text over scene background image
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
    print(f"Kinetic Reel successfully generated -> {output_path}")
