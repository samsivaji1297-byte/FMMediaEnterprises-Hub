import os
from moviepy import (
    AudioFileClip, 
    TextClip, 
    ColorClip, 
    CompositeVideoClip, 
    concatenate_videoclips
)

def build_video(script_data: dict, audio_path: str, output_path: str = "final_reel.mp4"):
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    scenes = script_data.get("scenes", [])
    scene_count = len(scenes)
    duration_per_scene = total_duration / max(scene_count, 1)
    
    clips = []
    
    for i, scene in enumerate(scenes):
        bg = ColorClip(size=(1080, 1920), color=(15, 15, 15), duration=duration_per_scene)
        
        txt_overlay = scene.get("text_overlay", "").upper()
        
        # MoviePy 2.x API parameters
        txt_clip = TextClip(
            text=txt_overlay,
            font_size=70,
            color='white',
            font='Arial-Bold',
            method='caption',
            size=(900, None)
        ).with_duration(duration_per_scene).with_position('center')
        
        scene_composite = CompositeVideoClip([bg, txt_clip])
        clips.append(scene_composite)
        
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.with_audio(audio)
    
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4
    )
    print(f"Reel successfully generated -> {output_path}")
