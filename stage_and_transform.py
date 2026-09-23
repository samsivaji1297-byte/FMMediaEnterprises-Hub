import os
import re
from google import genai
from google.genai.errors import APIError

def load_latest_research() -> str:
    """Reads the persisted research intelligence from disk."""
    research_path = os.path.join("ResearchFactory", "latest_research.md")
    if not os.path.exists(research_path):
        raise FileNotFoundError(f"Research file not found at {research_path}. Run research_engine.py first.")
    
    with open(research_path, "r", encoding="utf-8") as f:
        return f.read()

def generate_multi_asset_content():
    print("[INFO] Initializing Stage & Transform Engine...")
    
    # 1. Read context off disk (Zero web/tool call overhead)
    research_context = load_latest_research()
    print("[INFO] Successfully loaded persisted research context from disk.")

    # 2. Construct Single-Pass Prompt
    prompt = f"""
You are the lead content architect for theFINALMindset and FMMediaEnterprises.
Using the provided SEO Research Intelligence, generate three distinct, high-impact content assets in a SINGLE output.

You MUST separate each asset with the exact string delimiters shown below:

===BLOGGER_POST===
(Write an authoritative, SEO-optimized Blogger article with H2/H3 headers, clear key takeaways, and a call to action. Return ONLY the article content.)

===SUBSTACK_ESSAY===
(Write a deep, narrative-driven Substack essay with high analytical depth, compelling personal/systemic insights, and newsletter formatting. Return ONLY the essay content.)

===THREADS_SEQUENCE===
(Write a high-hook, 5 to 7 post Threads/X sequence with line breaks, tactical takeaways, and sharp punchy delivery. Return ONLY the thread posts.)

RESEARCH INTELLIGENCE CONTEXT:
{research_context}
"""

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    # 3. Execute 1 Single Gemini Call
    client = genai.Client(api_key=api_key)
    print("[INFO] Sending single-pass prompt to Gemini (gemini-2.5-flash)...")
    
    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt
    )

    raw_output = response.text
    print("[SUCCESS] Content assets generated successfully. Parsing payload...")

    # 4. Parse Delimiters & Save Individual Assets
    output_dir = "DistributionPlatforms"
    os.makedirs(output_dir, exist_ok=True)

    def extract_section(delimiter_name, text):
        pattern = f"==={delimiter_name}===\n(.*?)(?=\n===|\Z)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    blogger_content = extract_section("BLOGGER_POST", raw_output)
    substack_content = extract_section("SUBSTACK_ESSAY", raw_output)
    threads_content = extract_section("THREADS_SEQUENCE", raw_output)

    # Fallback writing if regex match hits unexpected output formatting
    if not blogger_content:
        blogger_content = raw_output

    with open(os.path.join(output_dir, "blogger.md"), "w", encoding="utf-8") as f:
        f.write(blogger_content)
    print("[SUCCESS] Persisted 'DistributionPlatforms/blogger.md'")

    if substack_content:
        with open(os.path.join(output_dir, "substack.md"), "w", encoding="utf-8") as f:
            f.write(substack_content)
        print("[SUCCESS] Persisted 'DistributionPlatforms/substack.md'")

    if threads_content:
        with open(os.path.join(output_dir, "threads.md"), "w", encoding="utf-8") as f:
            f.write(threads_content)
        print("[SUCCESS] Persisted 'DistributionPlatforms/threads.md'")

if __name__ == "__main__":
    generate_multi_asset_content()
