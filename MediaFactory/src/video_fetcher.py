import os
import random
import requests
from pathlib import Path
from urllib.parse import quote

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache" / "videos"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _generate_solid_fallback_video(output_path: Path) -> str:
    """Creates a local solid-state fallback video using PIL / MoviePy if Pexels is unreachable,
    guaranteeing a stunning obsidian background instead of a black screen."""
    try:
        from moviepy.editor import ColorClip
        # Create a 1080x1920 vertical solid obsidian dark slate background (RGB: 15, 17, 23)
        clip = ColorClip(size=(1080, 1920), color=(15, 17, 23), duration=5.0)
        clip.write_videotofile(str(output_path), fps=24, codec="libx264", audio=False, logger=None)
        print(f"[✓] Generated bulletproof solid obsidian fallback video: {output_path.name}")
        return str(output_path)
    except Exception as e:
        print(f"[!] Critical fallback video generation error: {e}")
        return ""


def fetch_background_video(query: str, scene_index: int, duration: float) -> str:
    """Fetches vertical HD stock footage from Pexels with strict fallback to guaranteed obsidian background."""
    api_key = os.getenv("PEXELS_API_KEY")
    output_path = CACHE_DIR / f"bg_video_{scene_index}.mp4"

    print(f"\n[DEBUG B-ROLL] Fetching for scene {scene_index + 1} | Query: '{query}'")

    if not api_key:
        print("[!] ERROR: PEXELS_API_KEY environment variable is NOT set or EMPTY. Using obsidian fallback.")
        return _generate_solid_fallback_video(output_path)

    clean_query = "".join(c for c in query if c.isalnum() or c.isspace()).strip()
    if not clean_query:
        clean_query = "dark abstract motion"

    search_queries = [
        f"dark {clean_query}",
        f"{clean_query} aesthetic vertical",
        "dark moody motion background",
        "cinematic abstract dark loop",
    ]

    headers = {"Authorization": api_key}

    for search_term in search_queries:
        encoded_query = quote(search_term)
        url = f"https://api.pexels.com/videos/search?query={encoded_query}&orientation=portrait&per_page=12"
        
        try:
            print(f"[*] Querying Pexels API for: '{search_term}'...")
            res = requests.get(url, headers=headers, timeout=10)
            
            if res.status_code != 200:
                print(f"[!] Pexels HTTP Error {res.status_code}")
                continue

            data = res.json()
            videos = data.get("videos", [])
            print(f"    Found {len(videos)} videos for query '{search_term}'.")

            if videos:
                selected_video = random.choice(videos[:min(len(videos), 5)])
                video_files = selected_video.get("video_files", [])

                if not video_files:
                    continue

                valid_files = [f for f in video_files if f.get("link")]
                if valid_files:
                    hd_file = max(valid_files, key=lambda x: x.get("width", 0) * x.get("height", 0))
                else:
                    hd_file = None

                if hd_file and "link" in hd_file:
                    video_url = hd_file["link"]
                    print(f"[✓] Downloading selected Pexels clip...")

                    video_res = requests.get(video_url, timeout=25, stream=True)
                    if video_res.status_code == 200:
                        with open(output_path, "wb") as f:
                            for chunk in video_res.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        file_size = output_path.stat().st_size
                        if file_size > 50000:
                            print(f"[✓] Saved B-Roll clip: {output_path.name} ({file_size / (1024*1024):.2f} MB)")
                            return str(output_path)
        except Exception as e:
            print(f"[!] Exception during Pexels fetch: {e}")

    print(f"[!] Pexels fetch exhausted for scene {scene_index + 1}. Deploying obsidian solid-state fallback.")
    return _generate_solid_fallback_video(output_path)
