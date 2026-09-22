import os
import sys
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
        f"[DEBUG WARN] API Rate Limit hit. Pausing {retry_state.next_action.sleep:.1f}s before retrying standard generation..."
    )
)
def call_standard_gemini(client, prompt: str):
    """Executes standard Gemini generation wrapped in retry backoff."""
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )
    return response.text

def run_research(topic: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(api_key=api_key)
    print("[DEBUG] Gemini client initialized successfully.")

    prompt = (
        f"Conduct deep, strategic research on the following topic: '{topic}'.\n\n"
        "Provide a comprehensive, highly actionable summary covering:\n"
        "1. Core concepts & foundational principles\n"
        "2. Strategic execution steps\n"
        "3. Key takeaways and actionable insights\n"
    )

    research_output = None

    # Step 1: Attempt Grounded Search
    print(f"[DEBUG] Starting Search-Grounded Research for: '{topic}'...")
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config={"tools": [{"google_search": {}}]}
        )
        research_output = response.text
        print("[DEBUG] Search-Grounded Research completed successfully.")

    except Exception as e:
        print(f"[DEBUG WARN] Grounded search hit an API limit: {e}")
        print("[DEBUG] Switching immediately to Fallback Mode (Standard Generation)...")

    # Step 2: Fallback to Standard Generation if Search failed
    if not research_output:
        print("[DEBUG] Running Standard Gemini Generation with Retry Protection...")
        # Brief pause before attempting fallback call
        time.sleep(5)
        research_output = call_standard_gemini(client, prompt)
        print("[DEBUG] Standard Generation completed successfully.")

    # Save output to file
    output_file = "research_summary.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(research_output)

    print(f"[DEBUG] Research summary successfully saved to '{output_file}'.")

if __name__ == "__main__":
    topic_input = sys.argv[1] if len(sys.argv) > 1 else "High Agency Mindset and Systemic Execution"
    run_research(topic_input)
