import os
import json
import time
from google import genai
from google.genai import types
from PIL import Image
import io
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Helper function to call generate_content with retries
@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=4, max=20),
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
    You are an elite Instagram Reels content producer. Create a high-retention 15-25 second vertical reel script about: "{topic}".
    
    Respond strictly in raw JSON with no markdown block formatting.
    Use this exact JSON schema:
    {{
        "title": "Short title",
        "voiceover_full": "Full voiceover text concatenated",
        "scenes": [
            {{
                "scene_id": 1,
                "narration": "Text spoken in this exact scene",
                "visual_prompt": "Cinematic vertical 9:16 high contrast photography prompt for AI image generation representing this concept, dark aesthetic, minimalist, 8k",
                "text_overlay": "SHORT IMPACTFUL PHRASE (MAX 3 WORDS)"
            }}
        ]
    }}
    """
    
    print("Calling Gemini API for script generation...")
    response = call_gemini_with_retry(client, prompt)
    script_data = json.loads(response.text)
    
    # Generate background images for each scene
    print("Generating AI visual backgrounds for scenes...")
    for i, scene in enumerate(script_data.get("scenes", [])):
        visual_prompt = scene.get("visual_prompt")
        print(f"Generating image {i+1}/{len(script_data['scenes'])}: '{visual_prompt[:40]}...'")
        
        try:
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
            image = Image.open(io.BytesIO(image_bytes))
            image = image.resize((1080, 1920))
            img_path = f"scene_{i}.jpg"
            image.save(img_path)
            scene["image_path"] = img_path
        except Exception as e:
            print(f"Warning: Image generation failed for scene {i+1} ({e}). Falling back to dark canvas.")
            scene["image_path"] = None

    return script_data
