import os
import time
import random
from typing import Callable, Any
from google import genai
from google.genai.errors import APIError

# --- Gemini Flash Model Chain (Primary to Fallbacks) ---
FLASH_MODEL_CASCADE = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
]

# Dedicated model dictionary for direct targeting
GEMINI_MODELS = {
    "flash_3_5": "gemini-3.5-flash",
    "flash_3_6": "gemini-3.6-flash",
    "flash_3_7": "gemini-3.7-flash",
    "flash_3_8": "gemini-3.8-flash",
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
    max_retries_per_model: int = 3, 
    initial_delay: float = 2.0, 
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
            except APIError as e:
                is_rate_limit = getattr(e, "code", None) == 429 or "429" in str(e)
                is_server_error = getattr(e, "code", None) in (500, 503) or any(code in str(e) for code in ["500", "503"])
                
                if is_rate_limit or is_server_error:
                    if attempt < max_retries_per_model:
                        # Exponential Backoff with Jitter
                        jittered_delay = delay * (0.5 + random.random())
                        print(f"[{model}][429/5xx Spike] Retry {attempt}/{max_retries_per_model} in {jittered_delay:.2f}s...")
                        time.sleep(jittered_delay)
                        delay *= backoff_factor
                    else:
                        print(f"[{model}] Retries exhausted. Escalating to next fallback model in cascade...")
                else:
                    raise e
            except Exception as e:
                raise e

    raise RuntimeError(f"All model fallbacks exhausted: {model_chain}")
