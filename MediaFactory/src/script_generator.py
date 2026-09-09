import os
import json
from google import genai
from google.genai import types

def generate_reel_content(topic: str) -> dict:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    You are an elite short-form content producer. Create a viral 15-30 second vertical reel script about: "{topic}".

    Respond strictly in raw JSON with no markdown block formatting.
    Use this exact JSON schema:
    {{
        "title": "Short title",
        "voiceover_full": "Full voiceover text concatenated",
        "scenes": [
            {{
                "scene_id": 1,
                "narration": "Text spoken in this exact frame",
                "visual_description": "Detailed image generation prompt describing a dramatic minimalist scene",
                "text_overlay": "SHORT ON-SCREEN TEXT (MAX 4 WORDS)"
            }}
        ]
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)
