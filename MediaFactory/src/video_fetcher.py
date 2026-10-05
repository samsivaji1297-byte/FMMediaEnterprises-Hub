import os
import random
import requests
from pathlib import Path

# Resolve cache directory relative to MediaFactory
BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache" / "videos"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_background_video(query: str, scene_index: int, duration: float) -> str:
    """Fetches vertical HD stock footage from Pexels based on search keywords."""
    api_key = os.getenv("PEXELS_API_KEY")
    output_path = CACHE_DIR / f"bg_video_{scene_index}.mp4"

    # Clean up old cached clip for this scene index if it exists
    if output_path.exists():
        try:
            output_path.unlink()
        except Exception:
            pass

    if not api_key:
        print("[!] PEXELS_API_KEY missing in environment. Falling back to solid canvas.")
        return ""

    # Search queries tailored for high-retention dark aesthetics
    dark_queries = [
        f"dark {query}",
        f"{query} vertical",
        "city night lights vertical",
        "dark moody street motion",
        "cinematic dark traffic light trails",
        "dark abstract motion background",
    ]

    headers = {"Authorization": api_key}

    for search_term in dark_queries:
        url = f"https://api.pexels.com/videos/search?query={search_term}&orientation=portrait&per_page=15"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                videos = data.get("videos", [])
                if videos:
                    selected_video = random.choice(videos[:5])
                    video_files = selected_video.get("video_files", [])

                    # Priority 1: Pick vertical clip where height > width
                    hd_file = next(
                        (
                            f for f in video_files
                            if f.get("height", 0) > f.get("width", 0) and f.get("width", 0) >= 720
                        ),
                        None,
                    )

                    # Priority 2: Any video file available
                    if not hd_file and video_files:
                        hd_file = video_files[0]

                    if hd_file and "link" in hd_file:
                        video_url = hd_file["link"]
                        print(f"[*] Downloading Pexels B-Roll for scene {scene_index + 1} ('{search_term}')...")
                        
                        video_res = requests.get(video_url, timeout=30, stream=True)
                        if video_res.status_code == 200:
                            with open(output_path, "wb") as f:
                                for chunk in video_res.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            return str(output_path)
        except Exception as e:
            print(f"[!] Pexels fetch error for query '{search_term}': {e}")

    print(f"[!] Warning: Could not download video from Pexels for scene {scene_index + 1}.")
    return ""
