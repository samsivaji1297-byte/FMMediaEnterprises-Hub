import os
import json
import time
from google import genai
from google.genai import types
from PIL import Image
import io
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import ClientError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=3, min=10, max=60),
    reraise=True
)
def call_gemini_with_retry(client, prompt):
    return client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

def generate_reel_content(topic: str) -> dict:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    You are an elite Instagram Reels content producer. Create a high-retention 15-20 second vertical reel script about: "{topic}".
    
    CRITICAL: Keep the output strictly to EXACTLY 3 scenes.
    
    Respond strictly in raw JSON with no markdown block formatting.
    Use this exact JSON schema:
    {{
        "title": "Short title",
        "voiceover_full": "Full voiceover text concatenated",
        "scenes": [
            {{
                "scene_id": 1,
                "narration": "Text spoken in this exact scene",
                "visual_prompt": "Cinematic vertical 9:16 high contrast dark aesthetic minimalist",
                "text_overlay": "SHORT IMPACTFUL PHRASE"
            }}
        ]
    }}
    """
    
    print("Calling Gemini API for script generation...")
    try:
        response = call_gemini_with_retry(client, prompt)
        script_data = json.loads(response.text)
    except ClientError as e:
        print(f"Gemini API Quota Exceeded (429). Utilizing fallback local script architecture.")
        # Fallback script payload so execution never dies on API throttle
        script_data = {
            "title": topic.upper(),
            "voiceover_full": f"Identity is not what you say. It is what you execute daily when no one is watching. Build systems. Reclaim sovereignty.",
            "scenes": [
                {"scene_id": 1, "narration": "Identity is not what you say.", "text_overlay": "IDENTITY IS EXECUTION"},
                {"scene_id": 2, "narration": "It is what you execute daily when no one is watching.", "text_overlay": "SILENT WORK"},
                {"scene_id": 3, "narration": "Build systems. Reclaim sovereignty.", "text_overlay": "RECLAIM SOVEREIGNTY"}
            ]
        }
    
    # Image Generation Block with Graceful 429 Catching
    for i, scene in enumerate(script_data.get("scenes", [])):
        visual_prompt = scene.get("visual_prompt", "dark aesthetic")
        print(f"Processing background layer for scene {i+1}/3...")
        
        # Skip Imagen call if we know we are on quota limit; fallback directly to canvas/Pexels
        try:
            time.sleep(2)  # Space out calls
            img_response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=visual_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="9:16",
                    person_generation="ALLOW_ADULT"
                )
            )
            image_bytes = img_response.generated_images[0].image.image_bytes
            image = Image.open(io.BytesIO(image_bytes)).resize((1080, 1920))
            img_path = f"scene_{i}.jpg"
            image.save(img_path)
            scene["image_path"] = img_path
        except Exception as e:
            print(f"Notice: Image API skipped or throttled ({e}). Pipeline using motion video / dark canvas fallback.")
            scene["image_path"] = None

    return script_data
