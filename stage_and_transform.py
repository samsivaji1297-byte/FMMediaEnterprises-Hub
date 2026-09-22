import os
import glob
import re
import time
from google import genai
from google.genai import errors
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

MODEL_ID = "gemini-1.5-flash"
RESEARCH_DIR = "ResearchFactory"

# Target distribution directories
DIST_BASE = "DistributionPlatforms"
BLOGGER_DIR = os.path.join(DIST_BASE, "Blogger")
SUBSTACK_DIR = os.path.join(DIST_BASE, "Substack")
LINKEDIN_DIR = os.path.join(DIST_BASE, "LinkedIn")

def get_latest_brief_path() -> str:
    """Finds the most recent research brief file in ResearchFactory."""
    files = glob.glob(os.path.join(RESEARCH_DIR, "*.md"))
    if not files:
        raise FileNotFoundError(f"No research briefs found in '{RESEARCH_DIR}'. Run research_engine.py first.")
    latest_file = max(files, key=os.path.getmtime)
    print(f"[DEBUG] Found latest research brief: {latest_file}")
    return latest_file

def extract_clean_title(brief_content: str, fallback_filename: str) -> str:
    """Extracts a clean post title from the brief H1 or Title Tag Options."""
    title_match = re.search(r'Option 1:\*\*?\s*(.+)', brief_content)
    if title_match:
        return title_match.group(1).strip()
    
    h1_match = re.search(r'^#\s*(.+)', brief_content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).replace("Executive SEO Brief:", "").strip()

    base = os.path.basename(fallback_filename)
    clean_base = re.sub(r'^SEO_Brief_', '', base)
    clean_base = re.sub(r'_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.md$', '', clean_base)
    return clean_base.replace('_', ' ').title()

# Catches both 503 ServerErrors and 429 Rate Limits / Quotas, backing off up to 45s
@retry(
    stop=stop_after_attempt(8),
    wait=wait_exponential(multiplier=2, min=10, max=60),
    retry=retry_if_exception_type((errors.ServerError, errors.APIError, errors.ClientError)),
    before_sleep=lambda retry_state: print(f"[DEBUG WARN] API Rate Limit or Server Busy. Waiting {retry_state.next_action.sleep:.1f}s before retrying...")
)
def call_gemini_with_retry(client, prompt: str):
    """Calls Gemini with exponential backoff on rate limits or server errors."""
    chat = client.chats.create(model=MODEL_ID)
    return chat.send_message(prompt)

def generate_asset_variant(client, prompt: str, output_path: str, asset_name: str):
    """Utility to call Gemini, save markdown, and throttle requests."""
    print(f"[DEBUG] Generating {asset_name} asset...")
    
    response = call_gemini_with_retry(client, prompt)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text.strip())
    print(f"[SUCCESS] Saved {asset_name} -> {output_path}")
    
    # 10-second pause between asset generations to preserve free-tier request quotas
    time.sleep(10)

def transform_brief_to_multi_assets(brief_file_path: str):
    """Transforms a single research brief into 3 distinct native channel assets."""
    with open(brief_file_path, "r", encoding="utf-8") as f:
        brief_content = f.read()

    clean_title = extract_clean_title(brief_content, brief_file_path)
    print(f"\n=== Mutating Brief for Title: '{clean_title}' ===")

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    slug = re.sub(r'[^\w\-_]', '_', clean_title.replace(" ", "_"))

    # 1. BLOGGER / SEO ARTICLE -> DistributionPlatforms/Blogger
    blogger_prompt = f"""
You are an expert SEO content strategist and technical writer.
Transform this research brief into a 1500+ word, highly actionable SEO article.

TITLE: # {clean_title}

INSTRUCTIONS:
- Follow the H2/H3 architecture from the brief.
- Write with high operational depth, include markdown comparison tables, and avoid generic AI filler.
- Optimize for high reader retention and clear search intent resolution.

RESEARCH BRIEF:
{brief_content}
"""
    blogger_file = os.path.join(BLOGGER_DIR, f"{slug}.md")
    generate_asset_variant(client, blogger_prompt, blogger_file, "Blogger SEO Post")

    # 2. SUBSTACK NEWSLETTER ESSAY -> DistributionPlatforms/Substack
    substack_prompt = f"""
You are a top-tier Substack essayist and strategic thinker.
Transform this research brief into an engaging, narrative-driven newsletter essay.

TITLE: {clean_title}

INSTRUCTIONS:
- Tone: Direct, intellectually rigorous, conversational, first-principles mindset.
- Structure: Start with a strong hook/real-world problem, break down the core framework, and end with a strategic takeaway.
- Use bold emphasis, short paragraphs, and callout boxes (`> blockquotes`) for key principles.

RESEARCH BRIEF:
{brief_content}
"""
    substack_file = os.path.join(SUBSTACK_DIR, f"{slug}.md")
    generate_asset_variant(client, substack_prompt, substack_file, "Substack Essay")

    # 3. LINKEDIN NATIVE FEED POST -> DistributionPlatforms/LinkedIn
    linkedin_prompt = f"""
You are a LinkedIn content creator known for high-agency operational insights.
Transform this research brief into a punchy, highly shareable LinkedIn post.

INSTRUCTIONS:
- Length: Under 2,000 characters.
- Formatting: Short single lines, strong spacing, clean emoji bullet points.
- Hook: Start with a strong non-obvious statement about: {clean_title}.
- Body: 3-4 tactical bullet points stripping the core philosophy down to execution.
- Call to Action: End with a direct question to trigger comments.

RESEARCH BRIEF:
{brief_content}
"""
    linkedin_file = os.path.join(LINKEDIN_DIR, f"{slug}.md")
    generate_asset_variant(client, linkedin_prompt, linkedin_file, "LinkedIn Post")

if __name__ == "__main__":
    brief_path = get_latest_brief_path()
    transform_brief_to_multi_assets(brief_path)
    print("\n=== Mutation Engine Complete: Assets routed to DistributionPlatforms/ ===")
