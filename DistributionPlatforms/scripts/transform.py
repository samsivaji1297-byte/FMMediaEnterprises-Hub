import os
import glob
import json
import yaml
from google import genai
from google.genai import types

# Initialize Gemini Client (reads GEMINI_API_KEY from environment)
client = genai.Client()

SYSTEM_PROMPT = """
You are an expert content adapter.
Transform the raw text into a high-impact Substack Note.
- Concise, high-signal micro-essay (100-250 words).
- Short paragraphs, clear spacing.
Return strictly valid JSON with key: "substack_note".
"""

def process_ready_files():
    # Search for Markdown drafts inside WritingFactory/
    files = glob.glob("WritingFactory/*.md")
    if not files:
        print("No markdown files found in WritingFactory/. Skipping.")
        return

    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        parts = content.split("---")
        if len(parts) < 3:
            raw_text = content
            status = "ready"
        else:
            metadata = yaml.safe_load(parts[1]) or {}
            raw_text = "---".join(parts[2:])
            status = metadata.get("status", "ready")

        if status == "ready":
            print(f"Processing payload for: {filepath}")
            prompt = f"{SYSTEM_PROMPT}\n\nRAW INPUT:\n{raw_text}"
            
            # Using model required by API environment
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Write payload directly to repo root dist/ folder
            dist_dir = os.path.abspath("dist")
            os.makedirs(dist_dir, exist_ok=True)
            output_file = os.path.join(dist_dir, "latest_payload.json")
            
            with open(output_file, "w", encoding="utf-8") as out:
                out.write(response.text)
                
            print(f"Payload successfully generated and saved to {output_file}")
            break

if __name__ == "__main__":
    process_ready_files()
