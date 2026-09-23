import os
import sys
import datetime
import slugify
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

def slugify_topic(topic: str) -> str:
    """Creates a clean filename slug from topic string."""
    clean = "".join([c if c.isalnum() or c in (" ", "-", "_") else "" for c in topic])
    return clean.strip().lower().replace(" ", "_")

def run_seo_research(topic: str = "High Agency Mindset and Systemic Execution"):
    print(f"[INFO] Initiating SERP signal harvest for: '{topic}'")
    
    # 1. Harvest DuckDuckGo SERP results
    search_results = []
    try:
        # Utilizing ddgs context manager for clean network teardown
        with DDGS() as ddgs:
            # Query passed as positional argument, max_results explicitly named
            raw_results = list(ddgs.text(topic, max_results=7))
            
        if not raw_results:
            print("[WARN] DuckDuckGo returned no SERP results. Fallback triggered.")
        else:
            search_results = raw_results
            print(f"[SUCCESS] Scraped {len(search_results)} live search signals.")
            
    except Exception as e:
        print(f"[ERROR] DDGS scrape failed: {e}")
        print("[INFO] Proceeding with empty context fallback.")

    # 2. Build Markdown Document
    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    date_prefix = now.strftime("%Y-%m-%d")

    md_lines = [
        f"# SEO Research Signal: {topic}",
        f"**Generated:** {timestamp_str}",
        f"**Engine:** DuckDuckGo SERP Scraper (Decoupled)",
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

    # 3. Save to ResearchFactory Directory with Timestamp
    target_dir = "ResearchFactory"
    os.makedirs(target_dir, exist_ok=True)

    file_slug = slugify_topic(topic)
    filename = f"{date_prefix}_{file_slug}.md"
    filepath = os.path.join(target_dir, filename)

    # Also maintain a latest pointer for downstream consumers
    latest_filepath = os.path.join(target_dir, "latest_research.md")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    with open(latest_filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"[SUCCESS] Research saved to '{filepath}'")
    print(f"[SUCCESS] Updated pointer '{latest_filepath}'")

if __name__ == "__main__":
    target_topic = sys.argv[1] if len(sys.argv) > 1 else "High Agency Mindset and Systemic Execution"
    run_seo_research(target_topic)
