import os
import time
import random
from typing import Callable, Any
from google import genai
from google.genai.errors import APIError
from groq import Groq

# --- Multi-Provider Fallback Cascade (Gemini Flash + Groq LPU Tiers) ---
# Tries cutting-edge Gemini flash models first, then falls back to ultra-fast Groq models.
HYBRID_MODEL_CASCADE = [
    # Primary Gemini Tier
    {"provider": "gemini", "model": "gemini-3.8-flash"},
    {"provider": "gemini", "model": "gemini-3.6-flash"},
    # Secondary Groq LPU Tier
    {"provider": "groq", "model": "llama-3.3-70b-versatile"},
    {"provider": "groq", "model": "llama-3.1-8b-instant"},
]

def get_client() -> genai.Client:
    """Initializes and returns the standardized GenAI Client instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")
    return genai.Client(api_key=api_key)

def get_groq_client() -> Groq:
    """Initializes and returns the Groq client instance if key is available."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing.")
    return Groq(api_key=api_key)

def call_with_fallback(
    gemini_api_func_builder: Callable[[str], Callable[[], Any]], 
    groq_api_func_builder: Callable[[str], Callable[[], Any]],
    model_chain: list[dict] = HYBRID_MODEL_CASCADE,
    max_retries_per_model: int = 3, 
    initial_delay: float = 2.0, 
    backoff_factor: float = 2.0
) -> Any:
    """
    Executes an API call cascading across different providers and models 
    with exponential backoff and jittered retry logic.
    """
    for tier in model_chain:
        provider = tier["provider"]
        model = tier["model"]
        
        # Select the correct builder function based on provider
        if provider == "gemini":
            api_func = gemini_api_func_builder(model)
        elif provider == "groq":
            # Safely skip groq tier if key is absent, or try to invoke
            if not os.getenv("GROQ_API_KEY"):
                print(f"[Skipping Groq Tier {model}] GROQ_API_KEY environment variable not found.")
                continue
            api_func = groq_api_func_builder(model)
        else:
            continue

        delay = initial_delay
        for attempt in range(1, max_retries_per_model + 1):
            try:
                print(f"[{provider.upper()}] Requesting generation using model: {model} (Attempt {attempt})")
                return api_func()
            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str or "rate limit" in err_str
                is_server_error = any(code in err_str for code in ["500", "502", "503", "504", "unavailable", "internal"])
                
                if is_rate_limit or is_server_error:
                    if attempt < max_retries_per_model:
                        jittered_delay = delay * (0.8 + random.random() * 0.4)
                        print(f"[{provider.upper()}:{model}][Spike/RateLimit] Retrying in {jittered_delay:.2f}s...")
                        time.sleep(jittered_delay)
                        delay *= backoff_factor
                    else:
                        print(f"[{provider.upper()}:{model}] Retries exhausted. Cascading to next fallback tier...")
                else:
                    print(f"[!] Unhandled API error on {provider.upper()}:{model}: {e}")
                    raise e

    raise RuntimeError("All multi-provider fallbacks exhausted in cascade.")
