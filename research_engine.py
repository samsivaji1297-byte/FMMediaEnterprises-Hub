import sys
import os
from ddgs import DDGS

def harvest_friction(seed_query: str) -> str:
    """
    Queries DuckDuckGo targeting Reddit and Hacker News 
    to extract raw human psychological friction.
    """
    ddgs = DDGS()
    
    # Strip quotes if present to avoid over-constraining the search
    clean_query = seed_query.replace('"', '').strip()
    
    # Target raw human discussions directly
    forum_target = f'{clean_query} (site:reddit.com OR site:news.ycombinator.com)'
    
    print(f"[*] Ingesting raw human friction for: '{clean_query}'...")
    
    try:
        results = list(ddgs.text(forum_target, max_results=8))
    except Exception as e:
        print(f"[!] Primary search error: {e}. Falling back to standard query...")
        results = []

    if not results:
        print("[!] Sparse forum hits. Broadening search parameters...")
        results = list(ddgs.text(clean_query, max_results=8))

    # Build markdown output payload
    markdown_payload = f"# Raw Human Friction Signals: {clean_query}\n\n"
    markdown_payload += "```text\n"
    
    for item in results:
        markdown_payload += f"Title: {item.get('title', 'N/A')}\n"
        markdown_payload += f"URL: {item.get('href', 'N/A')}\n"
        markdown_payload += f"Body: {item.get('body', 'N/A')}\n\n"
        
    markdown_payload += "```\n"
    return markdown_payload

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "high agency mindset"
    payload = harvest_friction(query)
    
    with open("latest_research.md", "w", encoding="utf-8") as f:
        f.write(payload)
        
    print("[+] Successfully persisted friction dump to 'latest_research.md'.")
