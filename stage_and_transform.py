import os
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google import genai
from google.genai import errors

MODEL_ID = "gemini-3.6-flash"

@retry(
    stop=stop_after_attempt(8),
    wait=wait_exponential(multiplier=2, min=10, max=65),
    retry=retry_if_exception_type((errors.ServerError, errors.APIError, errors.ClientError)),
    before_sleep=lambda retry_state: print(
        f"[DEBUG WARN] API Rate Limit or Server Busy. Waiting {retry_state.next_action.sleep:.1f}s before retrying..."
    )
)
def call_gemini_with_retry(client, prompt: str):
    """Calls Gemini with exponential backoff on rate limits or server errors."""
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )
    return response.text

def generate_and_save(client, prompt: str, output_file: str, label: str):
    """Handles generating a specific asset variant with pacing and error handoff."""
    print(f"\n[DEBUG] Generating {label} asset...")
    # Pace executions to avoid bursting the RPM quota
    time.sleep(6)
    
    content = call_gemini_with_retry(client, prompt)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"[DEBUG] Successfully saved {label} asset to {output_file}")

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
        
    client = genai.Client(api_key=api_key)
    print("[DEBUG] Gemini client initialized for stage and transform.")

    # Read research input
    input_file = "research_summary.md"
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input research file '{input_file}' not found. Ensure research_engine.py ran successfully.")
        
    with open(input_file, "r", encoding="utf-8") as f:
        research_data = f.read()

    # Prompts for transformed media outputs
    blogger_prompt = (
        "You are an expert technical editor and content strategist. "
        "Transform the following research notes into an engaging, long-form, SEO-optimized blog post formatted in Markdown. "
        "Include an intriguing title, clear subheadings, and key actionable takeaways.\n\n"
        f"RESEARCH DATA:\n{research_data}"
    )

    substack_prompt = (
        "You are a thought leader writing a high-value newsletter. "
        "Transform the following research into an insightful, personal-style Substack essay formatted in Markdown. "
        "Focus on narrative flow, strong hooks, strategic perspectives, and a compelling call-to-action at the end.\n\n"
        f"RESEARCH DATA:\n{research_data}"
    )

    linkedin_prompt = (
        "You are a personal brand and executive strategist. "
        "Transform the following research into a concise, high-impact LinkedIn post formatted in Markdown. "
        "Use short, punchy paragraphs, bullet points for readability, relevant hashtags, and an engaging question to drive comments.\n\n"
        f"RESEARCH DATA:\n{research_data}"
    )

    # Sequential execution with backoff protection
    generate_and_save(client, blogger_prompt, "blogger.md", "Blogger Post")
    generate_and_save(client, substack_prompt, "substack.md", "Substack Essay")
    generate_and_save(client, linkedin_prompt, "linkedin.md", "LinkedIn Post")

    print("\n[DEBUG] All stage and transform assets generated successfully!")

if __name__ == "__main__":
    main()
