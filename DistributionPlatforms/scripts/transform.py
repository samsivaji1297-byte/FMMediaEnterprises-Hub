import os
import glob
import json
import yaml
from google import genai
from google.genai import types

# Initialize Gemini Client (reads GEMINI_API_KEY from env automatically)
client = genai.Client()

SYSTEM_PROMPT = """
You are an expert content adapter.
Transform the raw text into a high-impact Substack Note.
- Concise, high-signal micro-essay (100-250 words).
- Short paragraphs, clear spacing.
Return strictly valid JSON with key: "substack_note".
"""

def process_ready_files():
    # Look for files in WritingFactory/
    files = glob.glob("WritingFactory/*.md")
    if not files:
        print("No markdown files found in WritingFactory/.")
        return

    for filepath in files:
        with open(filepath, "r") as f:
            content = f.read()
            
        parts = content.split("---")
        if len(parts) < 3:
            # If no frontmatter, treat whole file as raw content
            raw_text = content
            status = "ready"
        else:
            metadata = yaml.safe_load(parts[1]) or {}
            raw_text = "---".join(parts[2:])
            status = metadata.get("status", "ready")

        if status == "ready":
            print(f"Processing payload for: {filepath}")
            prompt = f"{SYSTEM_PROMPT}\n\nRAW INPUT:\n{raw_text}"
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Save payload to dist/ (repo root)
            os.makedirs("dist", exist_ok=True)
            output_file = "dist/latest_payload.json"
            with open(output_file, "w") as out:
                out.write(response.text)
            print(f"Payload saved to {output_file}")
            break # Process first ready file

if __name__ == "__main__":
    process_ready_files()
