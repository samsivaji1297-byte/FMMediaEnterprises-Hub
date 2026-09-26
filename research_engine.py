import os
import sys
import re
import datetime

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

def slugify_topic(topic: str) -> str:
    """Creates a clean filename slug from a topic string using native Python stdlib."""
    clean = re.sub(r'[^a-zA-Z0-9]+', '_', topic.strip().lower())
    return clean.strip('_')

def run_seo_research(topic: str = "overwhelmed by productivity systems"):
    # Clean topic string to ensure DuckDuckGo handles the query cleanly
    clean_topic = topic.replace('"', '').strip()
    
    # Force search to target raw human discussions on community platforms
    forum_query = f'{clean_topic} (site:reddit.com OR site:news.ycombinator.com)'
    
    print(f"[INFO] Initiating human friction harvest for: '{clean_topic}'")
    print(f"[INFO] Search query: {forum_query}")
    
    search_results = []
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(forum_query, max_results=8))
            
            # Fallback to broad query if forum-specific hits are sparse
            if not raw_results:
                print("[WARN] Forum query returned sparse hits. Triggering broad query fallback...")
                raw_results = list(ddgs.text(clean_topic, max_results=8))
            
        if raw_results:
            search_results = raw_results
            print(f"[SUCCESS] Scraped {len(search_results)} live human friction signals.")
        else:
            print("[WARN] No live search signals captured.")
            
    except Exception as e:
        print(f"[ERROR] DDGS scrape failed: {e}")
        print("[INFO] Proceeding with empty context fallback.")

    # Build Markdown Document
    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    date_prefix = now.strftime("%Y-%m-%d")

    md_lines = [
        f"# SEO Research Signal: {clean_topic}",
        f"**Generated:** {timestamp_str}",
        f"**Engine:** DuckDuckGo Forum Friction Scraper (Decoupled)",
        "---",
        "",
        "## Harvested Search Results",
        ""
    ]

    if search_results:
        for idx, item in enumerate(search_results, start=1):
            title = item.get("title", "No Title")
            href = item.get("href", item.get("url", "N/A"))
            snippet = item.get("body", item.get("snippet", "No Snippet"))
            
            md_lines.append(f"### {idx}. {title}")
            md_lines.append(f"- **URL:** {href}")
            md_lines.append(f"- **Snippet:** {snippet}")
            md_lines.append("")
    else:
        md_lines.append("> No live web search results captured for this query.")
        md_lines.append("")

    md_lines.append("---")
    md_lines.append("## Raw Intelligence Context")
    md_lines.append("```text")
    for item in search_results:
        md_lines.append(f"Title: {item.get('title', '')}")
        md_lines.append(f"URL: {item.get('href', '')}")
        md_lines.append(f"Body: {item.get('body', '')}\n")
    md_lines.append("```")

    markdown_content = "\n".join(md_lines)

    # Save to ResearchFactory Directory with Timestamp
    target_dir = "ResearchFactory"
    os.makedirs(target_dir, exist_ok=True)

    file_slug = slugify_topic(clean_topic)
    filename = f"{date_prefix}_{file_slug}.md"
    filepath = os.path.join(target_dir, filename)

    # Maintain latest pointer for downstream asset engines
    latest_filepath = os.path.join(target_dir, "latest_research.md")

    # Write historical dated research file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    # Overwrite latest_research.md pointer
    with open(latest_filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"[SUCCESS] Historical research archived to '{filepath}'")
    print(f"[SUCCESS] Updated downstream pointer '{latest_filepath}'")

if __name__ == "__main__":
    target_topic = sys.argv[1] if len(sys.argv) > 1 else "overwhelmed by productivity systems"
    run_seo_research(target_topic)
