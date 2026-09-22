import sys
import os
import time
from google import genai
from google.genai import types

MODEL_ID = "gemini-3.6-flash"

def run_research(topic: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    
    client = genai.Client(api_key=api_key)
    print("[DEBUG] Gemini client initialized successfully.")

    prompt = f"Conduct grounded search research on: {topic}"

    # Try Grounded Search
    try:
        print(f"[DEBUG] Starting Search-Grounded Research for: '{topic}'...")
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}]
            )
        )
        return response.text
    except Exception as e:
        print(f"[DEBUG WARN] Grounded search hit an API limit: {e}")
        print("[DEBUG] Switching immediately to Fallback Mode (Standard Generation)...")

    # Brief delay before fallback
    time.sleep(5)

    # Fallback to Standard Generation
    try:
        print("[DEBUG] Running Standard Gemini Generation (No Search Tools)...")
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        print("[DEBUG] Standard generation completed successfully!")
        return response.text
    except Exception as e:
        print(f"[DEBUG ERROR] Standard generation failed: {e}")
        raise e

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "High Agency Mindset"
    run_research(topic)
