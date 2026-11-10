import os
import random
import requests
from pathlib import Path
from urllib.parse import quote

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache" / "videos"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_background_video(query: str, scene_index: int, duration: float) -> str:
    """Fetches vertical HD stock footage from Pexels based on search keywords with robust fallbacks."""
    api_key = os.getenv("PEXELS_API_KEY")
    output_path = CACHE_DIR / f"bg_video_{scene_index}.mp4"

    print(f"\n[DEBUG B-ROLL] Fetching for scene {scene_index + 1} | Query: '{query}'")

    if not api_key:
        print("[!] ERROR: PEXELS_API_KEY environment variable is NOT set or EMPTY.")
        return ""

    # Clean and sanitize base query
    clean_query = "".join(c for c in query if c.isalnum() or c.isspace()).strip()
    if not clean_query:
        clean_query = "dark abstract motion"

    # Robust query cascade ordered from specific to broad
    search_queries = [
        f"dark {clean_query}",
        f"{clean_query} aesthetic vertical",
        "dark moody motion background",
        "cinematic abstract dark loop",
        "cyberpunk digital code background",
    ]

    headers = {"Authorization": api_key}

    for search_term in search_queries:
        encoded_query = quote(search_term)
        url = f"https://api.pexels.com/videos/search?query={encoded_query}&orientation=portrait&per_page=15"
        
        try:
            print(f"[*] Querying Pexels API for: '{search_term}'...")
            res = requests.get(url, headers=headers, timeout=12)
            
            if res.status_code != 200:
                print(f"[!] Pexels HTTP Error {res.status_code}: {res.text}")
                continue

            data = res.json()
            videos = data.get("videos", [])
            print(f"    Found {len(videos)} videos for query '{search_term}'.")

            if videos:
                # Shuffle top results to ensure variety across runs
                selected_video = random.choice(videos[:min(len(videos), 8)])
                video_files = selected_video.get("video_files", [])

                if not video_files:
                    continue

                # Priority 1: Vertical HD clip (height > width)
                hd_file = next(
                    (
                        f for f in video_files
                        if f.get("height", 0) > f.get("width", 0) and f.get("link")
                    ),
                    None,
                )

                # Priority 2: Highest resolution available video file as fallback
                if not hd_file:
                    valid_files = [f for f in video_files if f.get("link")]
                    if valid_files:
                        # Sort by resolution (width * height) descending
                        hd_file = max(valid_files, key=lambda x: x.get("width", 0) * x.get("height", 0))

                if hd_file and "link" in hd_file:
                    video_url = hd_file["link"]
                    w = hd_file.get('width', 0)
                    h = hd_file.get('height', 0)
                    print(f"[✓] Selected video URL ({w}x{h}). Downloading...")

                    video_res = requests.get(video_url, timeout=35, stream=True)
                    if video_res.status_code == 200:
                        with open(output_path, "wb") as f:
                            for chunk in video_res.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        file_size = output_path.stat().st_size
                        if file_size > 50000:  # Ensure it's a valid file (>50KB)
                            print(f"[✓] Saved B-Roll clip: {output_path.name} ({file_size / (1024*1024):.2f} MB)")
                            return str(output_path)
                        else:
                            print(f"[!] Downloaded file too small ({file_size} bytes), likely corrupted. Retrying...")
                    else:
                        print(f"[!] Video file download failed with status {video_res.status_code}")
        except Exception as e:
            print(f"[!] Exception during Pexels fetch for '{search_term}': {e}")

    print(f"[!] Could not retrieve any valid video from Pexels for scene {scene_index + 1}. Falling back to solid color.")
    return ""
