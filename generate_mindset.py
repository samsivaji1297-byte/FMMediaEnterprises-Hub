import sys
import datetime
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo
from google.genai import types

# Resolve project root path for clean config imports
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import get_client, get_groq_client, call_with_fallback

# --- Configuration & Directories ---
OUTPUT_DIR = PROJECT_ROOT / "WritingFactory" / "Mindset"

client = get_client()
try:
    groq_client = get_groq_client()
except Exception:
    groq_client = None


def build_prompt() -> str:
    """Constructs prompt for minimal operational mindset writing."""
    return """
Write 250–350 words of minimal, operational mindset guidance.

Constraints:
- Tone: calm, practical, grounded.
- Focus on: mentality, daily execution, cognitive hygiene, emotional regulation, decision clarity.
- Everyday-readable: no mythic language, no grandiose framing.
- Use simple, direct sentences.
- Break into 3–4 short paragraphs.
- Insert a blank line between each paragraph.
- No headings, no bullet points, no lists.
- No formatting.
"""


def generate_mindset() -> str:
    """Executes prompt against hybrid model cascade (Gemini -> Groq)."""
    prompt = build_prompt()

    # 1. Gemini Builder
    def _gemini_builder(target_model: str):
        def _call():
            gen_config = types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=gen_config,
            )
            text = response.text.strip()
            paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
            return "\n\n".join(paragraphs)
        return _call

    # 2. Groq Builder (OpenAI-compatible chat completion structure)
    def _groq_builder(target_model: str):
        def _call():
            if not groq_client:
                raise RuntimeError("Groq client not initialized.")
            
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an operational mindset coach writing calm, direct, and practical guidance."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=target_model,
                temperature=0.7,
            )
            text = chat_completion.choices[0].message.content.strip()
            paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
            return "\n\n".join(paragraphs)
        return _call

    return call_with_fallback(_gemini_builder, _groq_builder)


def save_output(text: str) -> Path:
    """Saves generated mindset piece into WritingFactory/Mindset with Sydney timestamp."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now(ZoneInfo("Australia/Sydney")).strftime("%Y-%m-%d_%H-%M-%S")
    filepath = OUTPUT_DIR / f"Mindset_{timestamp}.md"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Operational Mindset — {timestamp}\n\n{text}\n")

    print(f"Saved mindset writing: {filepath}")
    return filepath


def git_commit(filepath: Path) -> None:
    """Commits created mindset asset to local Git tracking using subprocess with auto-configured identity."""
    try:
        rel_filepath = filepath.relative_to(PROJECT_ROOT)
        
        # Ensure local git identity is configured to prevent 'Author identity unknown' errors
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)

        subprocess.run(["git", "add", str(rel_filepath)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Add Mindset writing: {rel_filepath.name}"], 
            check=True
        )
        print(f"[Git] Successfully committed {rel_filepath.name}")
    except Exception as e:
        print(f"[Git Warning] Automated commit skipped: {e}")


def main():
    print("Starting Mindset Writing Engine with Hybrid Multi-Provider Cascade...")
    mindset_text = generate_mindset()
    saved_filepath = save_output(mindset_text)
    git_commit(saved_filepath)


if __name__ == "__main__":
    main()
