import os
import sys
import time
from typing import Optional
from google import genai
from google.genai import types
from google.genai.errors import ClientError

# Configuration
MODEL_ID = "gemini-3.6-flash"  # Flash model has higher RPM/TPM thresholds
MAX_RETRIES = 5
INITIAL_BACKOFF = 12  # Seconds to wait on first 429 before retrying

def get_gemini_client() -> genai.Client:
    """Initializes and returns the Google Gen AI SDK Client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not found.", file=sys.stderr)
        sys.exit(1)
    return genai.Client(api_key=api_key)

def execute_chat_with_backoff(client: genai.Client, prompt: str, config: types.GenerateContentConfig):
    """
    Executes grounded research using the Chat module to comply with 
    Automatic Function Calling (AFC) SDK guidelines and handles 429 rate limits.
    """
    backoff = INITIAL_BACKOFF
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # AFC (Search Grounding) is properly supported on Chat sessions
            chat = client.chats.create(
                model=MODEL_ID,
                config=config
            )
            response = chat.send_message(prompt)
            return response
            
        except ClientError as e:
            if "429" in str(e) or e.code == 429:
                print(f"[Rate Limit 429] Quota exceeded. Retrying in {backoff}s... (Attempt {attempt}/{MAX_RETRIES})")
                time.sleep(backoff)
                backoff *= 2  # Exponential backoff
            else:
                print(f"[ClientError] API call failed: {e}", file=sys.stderr)
                raise e
        except Exception as e:
            print(f"[Unexpected Error]: {e}", file=sys.stderr)
            raise e

    raise RuntimeError(f"Failed to complete research after {MAX_RETRIES} attempts due to persistent rate limiting.")

def run_seo_research(target_topic: str) -> Optional[str]:
    """Runs search-grounded research on a target topic."""
    print(f"--- Running Google Search Grounded Research on: '{target_topic}' ---")
    
    client = get_gemini_client()
    
    # Configure Google Search Grounding tool
    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.3  # Keeps research output focused and accurate
    )
    
    prompt = (
        f"Perform structured research on the topic: '{target_topic}'. "
        f"Provide core insights, systemic execution steps, actionable takeaways, "
        f"and key domain terminology."
    )

    response = execute_chat_with_backoff(client, prompt, config)
    
    if response and response.text:
        print("\n=== Research Results ===")
        print(response.text)
        return response.text
    else:
        print("Warning: Received empty response from Gemini API.", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_topic = " ".join(sys.argv[1:])
    else:
        target_topic = "High Agency Mindset and Systemic Execution"
        
    run_seo_research(target_topic)
