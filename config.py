import os
import time
import random
from typing import Callable, Any
from google import genai
from google.genai.errors import APIError

# --- Gemini Flash Model Cascade (Active Production Endpoints) ---
FLASH_MODEL_CASCADE = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
]

# Dedicated model dictionary for direct targeting
GEMINI_MODELS = {
    "flash_3_8": "gemini-3.8-flash",
    "flash_3_6": "gemini-3.6-flash",
}

def get_client() -> genai.Client:
    """Initializes and returns the standardized GenAI Client instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")
    return genai.Client(api_key=api_key)

def call_with_fallback(
    api_func_builder: Callable[[str], Callable[[], Any]], 
    model_chain: list[str] = FLASH_MODEL_CASCADE,
    max_retries_per_model: int = 4, 
    initial_delay: float = 3.0, 
    backoff_factor: float = 2.0
) -> Any:
    """
    Executes an API call using a primary model with exponential backoff.
    If the model hits persistent 429 rate limits or transient errors, it 
    cascades down through the fallback model list until completion.
    """
    for model_index, model in enumerate(model_chain):
        delay = initial_delay
        api_func = api_func_builder(model)
        
        for attempt in range(1, max_retries_per_model + 1):
            try:
                # Attempt execution with current model in cascade
                return api_func()
            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str
                is_server_error = any(code in err_str for code in ["500", "502", "503", "504", "unavailable", "internal"])
                
                # If rate-limited or transient server error, execute backoff retry
                if is_rate_limit or is_server_error:
                    if attempt < max_retries_per_model:
                        jittered_delay = delay * (0.8 + random.random() * 0.4)
                        print(f"[{model}][RateLimit/ServerSpike] Retry {attempt}/{max_retries_per_model} in {jittered_delay:.2f}s...")
                        time.sleep(jittered_delay)
                        delay *= backoff_factor
                    else:
                        print(f"[{model}] Retries exhausted for this tier. Cascading to next fallback model...")
                else:
                    # Non-retryable error (e.g., bad parameter / auth failure) -> raise immediately
                    print(f"[!] Unhandled API error on {model}: {e}")
                    raise e

    raise RuntimeError(f"All model fallbacks exhausted in cascade: {model_chain}")
