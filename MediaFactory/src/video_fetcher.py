import os
import random
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache" / "videos"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_background_video(query: str, scene_index: int, duration: float) -> str:
    """Fetches vertical HD stock footage from Pexels based on search keywords."""
    api_key = os.getenv("PEXELS_API_KEY")
    output_path = CACHE_DIR / f"bg_video_{scene_index}.mp4"

    print(f"\n[DEBUG B-ROLL] Fetching for scene {scene_index + 1} | Query: '{query}'")

    if not api_key:
        print("[!] ERROR: PEXELS_API_KEY environment variable is NOT set or EMPTY.")
        return ""

    # Search queries tailored for high-retention dark aesthetics
    dark_queries = [
        f"dark {query}",
        f"{query} vertical",
        "dark moody street motion",
        "cinematic dark traffic light trails",
        "dark abstract motion background",
    ]

    headers = {"Authorization": api_key}

    for search_term in dark_queries:
        url = f"https://api.pexels.com/videos/search?query={search_term}&orientation=portrait&per_page=15"
        try:
            print(f"[*] Querying Pexels API for: '{search_term}'...")
            res = requests.get(url, headers=headers, timeout=10)
            
            if res.status_code != 200:
                print(f"[!] Pexels HTTP Error {res.status_code}: {res.text}")
                continue

            data = res.json()
            videos = data.get("videos", [])
            print(f"    Found {len(videos)} videos for query '{search_term}'.")

            if videos:
                selected_video = random.choice(videos[:5])
                video_files = selected_video.get("video_files", [])

                # Priority 1: Vertical clip where height > width
                hd_file = next(
                    (
                        f for f in video_files
                        if f.get("height", 0) > f.get("width", 0)
                    ),
                    None,
                )

                # Priority 2: Fallback to any video file
                if not hd_file and video_files:
                    hd_file = video_files[0]

                if hd_file and "link" in hd_file:
                    video_url = hd_file["link"]
                    print(f"[✓] Selected video URL ({hd_file.get('width')}x{hd_file.get('height')}). Downloading...")

                    video_res = requests.get(video_url, timeout=30, stream=True)
                    if video_res.status_code == 200:
                        with open(output_path, "wb") as f:
                            for chunk in video_res.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        file_size = output_path.stat().st_size
                        print(f"[✓] Saved B-Roll clip: {output_path} ({file_size / (1024*1024):.2f} MB)")
                        return str(output_path)
                    else:
                        print(f"[!] Video file download failed with status {video_res.status_code}")
        except Exception as e:
            print(f"[!] Exception during Pexels fetch for '{search_term}': {e}")

    print(f"[!] Could not retrieve any valid video from Pexels for scene {scene_index + 1}.")
    return ""
