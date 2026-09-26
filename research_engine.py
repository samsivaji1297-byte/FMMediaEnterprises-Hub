import sys
import os
from duckduckgo_search import DDGS

def harvest_friction(seed_query: str) -> str:
    """
    Queries DuckDuckGo specifically targeting Reddit and Hacker News 
    to extract raw human psychological friction and forum discussions.
    """
    ddgs = DDGS()
    
    # Force search to pull raw human discussion platforms
    forum_target = f'"{seed_query}" (site:reddit.com OR site:news.ycombinator.com)'
    
    print(f"[*] Ingesting raw human friction for: '{seed_query}'...")
    results = ddgs.text(forum_target, max_results=8)
    
    if not results:
        # Fallback to broader web search if forum results are sparse
        print("[!] Sparse forum hits. Broadening search parameters...")
        results = ddgs.text(seed_query, max_results=8)

    # Format the payload for latest_research.md persistence
    markdown_payload = f"# Raw Human Friction Signals: {seed_query}\n\n"
    markdown_payload += "```text\n"
    
    for item in results:
        markdown_payload += f"Title: {item.get('title', 'N/A')}\n"
        markdown_payload += f"URL: {item.get('href', 'N/A')}\n"
        markdown_payload += f"Body: {item.get('body', 'N/A')}\n\n"
        
    markdown_payload += "```\n"
    return markdown_payload

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "paralyzed by choice productivity tools"
    payload = harvest_friction(query)
    
    # Write output to latest_research.md
    with open("latest_research.md", "w", encoding="utf-8") as f:
        f.write(payload)
        
    print("[+] Successfully persisted friction dump to 'latest_research.md'.")
