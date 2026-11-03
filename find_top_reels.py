import sys
import json
import subprocess
import statistics

def get_profile_reels(username, max_posts=20):
    """Fetches metadata for the last N posts on a public Instagram profile using yt-dlp."""
    profile_url = f"https://www.instagram.com/{username.strip('@')}/reels/"
    
    print(f"Scanning profile: @{username} (Fetching up to {max_posts} recent Reels)...")
    
    # yt-dlp command to dump JSON metadata without downloading media
    cmd = [
        "yt-dlp",
        "--impersonate", "Chrome",
        "--dump-single-json",
        "--playlist-end", str(max_posts),
        profile_url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0 or not result.stdout:
        print("Error fetching profile metadata. Make sure the profile is public.")
        return []

    try:
        data = json.loads(result.stdout)
        entries = data.get("entries", [])
    except json.JSONDecodeError:
        print("Failed to parse JSON response from profile dump.")
        return []

    reels = []
    for entry in entries:
        if not entry:
            continue
        
        webpage_url = entry.get("webpage_url") or f"https://www.instagram.com/reel/{entry.get('id')}/"
        view_count = entry.get("view_count") or entry.get("play_count") or 0
        like_count = entry.get("like_count") or 0
        title = entry.get("title") or entry.get("description") or ""

        reels.append({
            "url": webpage_url,
            "views": view_count,
            "likes": like_count,
            "title": title[:40].strip().replace("\n", " ")
        })

    return reels

def find_top_outliers(reels, top_n=3):
    """Calculates median views and ranks top outlier Reels."""
    if not reels:
        return []

    # Sort reels by view count descending
    sorted_reels = sorted(reels, key=lambda x: x["views"], reverse=True)
    
    views_list = [r["views"] for r in reels if r["views"] > 0]
    median_views = statistics.median(views_list) if views_list else 1

    print(f"\n--- Baseline Stats ---")
    print(f"Total Reels Analyzed: {len(reels)}")
    print(f"Median View Count:   {int(median_views):,}\n")

    top_outliers = sorted_reels[:top_n]
    
    print(f"=== TOP {top_n} OUTLIER REELS ===")
    for idx, reel in enumerate(top_outliers, 1):
        multiplier = round(reel["views"] / median_views, 1) if median_views > 0 else 0
        print(f"{idx}. [{multiplier}x Median] {reel['views']:,} views | {reel['url']}")
        print(f"   Caption Hook: \"{reel['title']}...\"\n")

    return top_outliers

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_username = sys.argv[1]
    else:
        target_username = input("Enter target Instagram handle (e.g. instagram): ")

    reels = get_profile_reels(target_username, max_posts=20)
    top_reels = find_top_outliers(reels, top_n=3)
    
    # Save target URLs to a text file for the extraction workflow to ingest
    if top_reels:
        with open("top_urls.txt", "w") as f:
            for reel in top_reels:
                f.write(f"{reel['url']}\n")
        print("Saved top URLs to top_urls.txt")
