import os
import re
import io
import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
from google.genai import types

# --- Resolve Project Root & Path Configuration ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent if SCRIPT_DIR.name == "src" else SCRIPT_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import get_client, call_with_fallback

# Output destination directory for generated scene assets
OUTPUT_DIR = PROJECT_ROOT / "MediaFactory" / "output"

client = get_client()


def clean_json_text(text: str) -> str:
    """Strips markdown code fences and cleans raw LLM output for strict JSON parsing."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def build_script_prompt(topic: str) -> str:
    return f"""
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


def generate_reel_content(topic: str) -> dict:
    """
    Generates a structured Reel script using the config.py model cascade,
    and attempts background image layer generation via Imagen.
    """
    prompt = build_script_prompt(topic)

    def _api_call_builder(target_model: str):
        def _api_call():
            print(f"[*] Generating Reel script using model: {target_model}")
            
            gen_config = types.GenerateContentConfig(
                response_mime_type="application/json",
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )
            
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=gen_config,
            )
            return response.text.strip()
        return _api_call

    # 1. Execute script generation via centralized model cascade
    try:
        raw_response = call_with_fallback(_api_call_builder)
        script_data = json.loads(clean_json_text(raw_response))
    except Exception as e:
        print(f"[!] Primary generation failed or JSON parse error ({e}). Utilizing fallback local script architecture.")
        script_data = {
            "title": topic.upper(),
            "voiceover_full": f"Identity is not what you say. It is what you execute daily when no one is watching. Build systems. Reclaim sovereignty.",
            "scenes": [
                {"scene_id": 1, "narration": "Identity is not what you say.", "text_overlay": "IDENTITY IS EXECUTION", "visual_prompt": "dark aesthetic minimalist"},
                {"scene_id": 2, "narration": "It is what you execute daily when no one is watching.", "text_overlay": "SILENT WORK", "visual_prompt": "dark aesthetic minimalist"},
                {"scene_id": 3, "narration": "Build systems. Reclaim sovereignty.", "text_overlay": "RECLAIM SOVEREIGNTY", "visual_prompt": "dark aesthetic minimalist"}
            ]
        }

    # Prepare local output folder
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # 2. Image Generation Block with Graceful Catching & File Handling
    for i, scene in enumerate(script_data.get("scenes", [])):
        visual_prompt = scene.get("visual_prompt", "dark aesthetic minimalist high contrast")
        print(f"[*] Processing background layer for scene {i+1}/3...")
        
        try:
            time.sleep(1)  # Rate pacing
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
            
            if img_response and img_response.generated_images:
                image_bytes = img_response.generated_images[0].image.image_bytes
                image = Image.open(io.BytesIO(image_bytes)).resize((1080, 1920))
                
                img_file_path = OUTPUT_DIR / f"{timestamp}_scene_{i+1}.jpg"
                image.save(img_file_path)
                scene["image_path"] = str(img_file_path)
                print(f"[+] Saved background layer: {img_file_path.relative_to(PROJECT_ROOT)}")
            else:
                raise ValueError("No images returned from API call.")

        except Exception as e:
            print(f"[!] Notice: Image API skipped or throttled ({e}). Pipeline using motion video / dark canvas fallback.")
            scene["image_path"] = None

    return script_data


if __name__ == "__main__":
    test_topic = "Execution vs Strategy"
    print(f"Executing MediaFactory Script Generator for: '{test_topic}'")
    result = generate_reel_content(test_topic)
    print("\n--- Final Generated Script Output ---")
    print(json.dumps(result, indent=2))
