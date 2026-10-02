import os
import time
import random
from typing import Callable, Any
from google import genai
from google.genai.errors import APIError

# --- Gemini Model Family Matrix ---
GEMINI_MODELS = {
    # Default workhorse model
    "default": os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
    
    # 3.X Flash Series
    "flash_3_5": "gemini-3.5-flash",
    "flash_lite": "gemini-3.5-flash-lite",
    
    # Reasoning & Heavy Workloads
    "pro": "gemini-3.1-pro",
}

def get_model(tier: str = "default") -> str:
    """Safely retrieves a Gemini model identifier string by tier."""
    return GEMINI_MODELS.get(tier, GEMINI_MODELS["default"])

def get_client() -> genai.Client:
    """Initializes and returns the standardized GenAI Client instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")
    return genai.Client(api_key=api_key)

def call_with_retry(
    api_func: Callable[[], Any], 
    max_retries: int = 5, 
    initial_delay: float = 2.0, 
    backoff_factor: float = 2.0
) -> Any:
    """
    Executes an API call wrapped in an Exponential Backoff + Jitter retry loop
    to handle 429 Rate Limit spikes and transient API errors.
    """
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            return api_func()
        except APIError as e:
            # Catch 429 Too Many Requests or 503 Unavailable transient errors
            is_rate_limit = getattr(e, "code", None) == 429 or "429" in str(e)
            is_server_error = getattr(e, "code", None) == 503 or "503" in str(e)
            
            if (is_rate_limit or is_server_error) and attempt < max_retries:
                # Add full jitter to prevent synchronized thundering herds
                jittered_delay = delay * (0.5 + random.random())
                print(f"[Rate Limit / API Spike] Retrying attempt {attempt}/{max_retries} in {jittered_delay:.2f}s...")
                time.sleep(jittered_delay)
                delay *= backoff_factor
            else:
                raise e
        except Exception as e:
            raise e
