import os
import requests
import random

def fetch_background_video(query: str, scene_index: int, duration: float) -> str:
    api_key = os.getenv("PEXELS_API_KEY")
    output_path = f"bg_video_{scene_index}.mp4"
    
    # Fallback search queries tailored for high-retention dark aesthetics
    dark_queries = [
        f"dark {query}",
        "city night lights vertical",
        "dark moody street motion",
        "cinematic dark traffic light trails",
        "dark abstract motion background"
    ]
    
    headers = {"Authorization": api_key} if api_key else {}
    
    if api_key:
        for search_term in dark_queries:
            url = f"https://api.pexels.com/videos/search?query={search_term}&orientation=portrait&per_page=15"
            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    videos = data.get("videos", [])
                    if videos:
                        selected_video = random.choice(videos[:5])
                        # Find HD vertical video file
                        video_files = selected_video.get("video_files", [])
                        hd_file = next((f for f in video_files if f.get("width", 0) >= 720 and f.get("height", 0) >= 1280), None)
                        if not hd_file and video_files:
                            hd_file = video_files[0]
                            
                        if hd_file:
                            video_url = hd_file["link"]
                            print(f"Downloading background video motion clip from Pexels for query: '{search_term}'...")
                            video_res = requests.get(video_url, timeout=30)
                            with open(output_path, "wb") as f:
                                f.write(video_res.content)
                            return output_path
            except Exception as e:
                print(f"Pexels fetch error for query '{search_term}': {e}")
                
    print(f"Warning: Could not fetch video from API. Using local fallback.")
    return None
