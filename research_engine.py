import os
import sys
import re
import random
import datetime

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

# Default seeds used ONLY if seed_topics.txt does not exist
DEFAULT_SEEDS = [
    "paralyzed by choice productivity tools",
    "fear of failure starting side business 2026",
    "income control vs effort disconnect",
    "overwhelmed by too many productivity systems",
    "overthinking project launch perfectionism",
    "feeling stuck in career low agency"
]

def slugify_topic(topic: str) -> str:
    """Creates a clean filename slug from a topic string using native Python stdlib."""
    clean = re.sub(r'[^a-zA-Z0-9]+', '_', topic.strip().lower())
    return clean.strip('_')

def get_random_seed(seed_file: str = "seed_topics.txt") -> str:
    """
    Ensures seed_topics.txt exists, reads it, and randomly selects 1 topic.
    """
    if not os.path.exists(seed_file):
        print(f"[INFO] '{seed_file}' not found. Creating default seed file...")
        with open(seed_file, "w", encoding="utf-8") as f:
            f.write("\n".join(DEFAULT_SEEDS) + "\n")
        seeds = DEFAULT_SEEDS
    else:
        with open(seed_file, "r", encoding="utf-8") as f:
            seeds = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        if not seeds:
            print(f"[WARN] '{seed_file}' was empty. Populating defaults...")
            with open(seed_file, "w", encoding="utf-8") as f:
                f.write("\n".join(DEFAULT_SEEDS) + "\n")
            seeds = DEFAULT_SEEDS

    selected = random.choice(seeds)
    print(f"[SUCCESS] Selected Random Seed Topic: '{selected}'")
    return selected

def run_seo_research(topic: str = None):
    # Always pull a random seed if no explicit CLI parameter was given
    if not topic:
        topic = get_random_seed()

    clean_topic = topic.replace('"', '').strip()
    
    print(f"[INFO] Harvesting dual-layer intelligence for: '{clean_topic}'")
    
    web_results = []
    forum_results = []
    
    with DDGS() as ddgs:
        # 1. Harvest General Web SERP (5 Top Web Articles)
        try:
            print("[*] Fetching general web SERP signals...")
            web_results = list(ddgs.text(clean_topic, max_results=5))
        except Exception as e:
            print(f"[ERROR] Web search failed: {e}")

        # 2. Harvest Community Forum Signals (5 Reddit/Forum Threads)
        try:
            print("[*] Fetching community forum friction signals (Reddit)...")
            forum_query = f"{clean_topic} site:reddit.com"
            forum_results = list(ddgs.text(forum_query, max_results=5))
        except Exception as e:
            print(f"[ERROR] Forum search failed: {e}")

    # Build Markdown Document
    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    date_prefix = now.strftime("%Y-%m-%d")

    md_lines = [
        f"# SEO Research Signal: {clean_topic}",
        f"**Generated:** {timestamp_str}",
        f"**Engine:** DuckDuckGo Dual-Layer Scraper (Web + Forum Hybrid)",
        "---",
        "",
        "## 1. Web SERP Articles & Insights",
        ""
    ]

    if web_results:
        for idx, item in enumerate(web_results, start=1):
            title = item.get("title", "No Title")
            href = item.get("href", item.get("url", "N/A"))
            snippet = item.get("body", item.get("snippet", "No Snippet"))
            
            md_lines.append(f"### {idx}. {title}")
            md_lines.append(f"- **URL:** {href}")
            md_lines.append(f"- **Snippet:** {snippet}")
            md_lines.append("")
    else:
        md_lines.append("> No web SERP results captured.\n")

    md_lines.append("---")
    md_lines.append("## 2. Reddit Community Friction Signals")
    md_lines.append("")

    if forum_results:
        for idx, item in enumerate(forum_results, start=1):
            title = item.get("title", "No Title")
            href = item.get("href", item.get("url", "N/A"))
            snippet = item.get("body", item.get("snippet", "No Snippet"))
            
            md_lines.append(f"### {idx}. {title}")
            md_lines.append(f"- **URL:** {href}")
            md_lines.append(f"- **Snippet:** {snippet}")
            md_lines.append("")
    else:
        md_lines.append("> No Reddit community results captured.\n")

    md_lines.append("---")
    md_lines.append("## Raw Intelligence Context")
    md_lines.append("```text")
    md_lines.append("=== GENERAL WEB CONTEXT ===")
    for item in web_results:
        md_lines.append(f"Title: {item.get('title', '')}")
        md_lines.append(f"URL: {item.get('href', '')}")
        md_lines.append(f"Body: {item.get('body', '')}\n")

    md_lines.append("=== REDDIT FRICTION CONTEXT ===")
    for item in forum_results:
        md_lines.append(f"Title: {item.get('title', '')}")
        md_lines.append(f"URL: {item.get('href', '')}")
        md_lines.append(f"Body: {item.get('body', '')}\n")
    md_lines.append("```")

    markdown_content = "\n".join(md_lines)

    # 3. Save to ResearchFactory Directory with Date + Time Timestamp
    target_dir = "ResearchFactory"
    os.makedirs(target_dir, exist_ok=True)

    # Use Date AND Time timestamp so multiple daily runs don't overwrite
    datetime_prefix = now.strftime("%Y-%m-%d_%H%M%S")
    file_slug = slugify_topic(clean_topic)

    # Example filename: 2026-09-26_014530_paralyzed_by_choice_productivity_tools.md
    filename = f"{datetime_prefix}_{file_slug}.md"
    filepath = os.path.join(target_dir, filename)

    # Maintain latest pointer for downstream asset engines
    latest_filepath = os.path.join(target_dir, "latest_research.md")

    # Save unique timestamped archive file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    # Overwrite downstream latest_research.md pointer
    with open(latest_filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"[SUCCESS] Historical research saved to '{filepath}'")
    print(f"[SUCCESS] Downstream pointer updated at '{latest_filepath}'")

if __name__ == "__main__":
    cli_topic = sys.argv[1] if len(sys.argv) > 1 else None
    run_seo_research(cli_topic)
