import os
import re
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from google.genai import types

# Resolve project root path for clean config imports
PROJECT_ROOT = Path(__file__).resolve().parent
if PROJECT_ROOT.name == "scripts":
    PROJECT_ROOT = PROJECT_ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config import get_client, call_with_fallback

# --- Path Configurations ---
RESEARCH_PRIMARY_PATH = PROJECT_ROOT / "ResearchFactory" / "latest_research.md"
RESEARCH_FALLBACK_PATH = PROJECT_ROOT / "latest_research.md"
DISTRIBUTION_DIR = PROJECT_ROOT / "DistributionPlatforms"

client = get_client()

RECOGNITION_EVENT_PROMPT = """
You are an elite Content Architect specializing in "Recognition-Event" assets and friction-based human psychology.

You have been provided raw forum text scraped from high-context communities (Reddit/Hacker News).

Your Job:
1. Extract the core HUMAN FRICTION (the unspoken emotional/psychological bottleneck).
2. Identify the UNDERLYING MECHANISM (why this friction exists, e.g., Decision Fatigue, Fear of Effort-Income Disconnect).
3. Transform this insight into 3 distinct, high-converting assets separated by exact delimitations:

===THREADS_START===
[Insert 3-4 standalone punchy posts designed to be read sequentially on Threads/X. Include a 2-line Reel Hook & Caption at the top.]
===THREADS_END===

===SUBSTACK_START===
[Insert Substack Long-Form Essay (400-600 words) dissecting the psychological mechanism, titled with a high-agency curiosity hook.]
===SUBSTACK_END===

===BLOGGER_START===
[Insert Blogger/SEO Article optimized for search intent, entity coverage, and practical execution.]
===BLOGGER_END===

RAW FORUM DATA PAYLOAD:
{raw_data_payload}
"""


def extract_section(content: str, tag_name: str) -> str:
    """Extracts content between explicit delimiters using regex first, falling back to string splitting."""
    pattern = rf"===\s*{tag_name}_START\s*===\s*(.*?)\s*===\s*{tag_name}_END\s*==="
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    start_delim = f"==={tag_name}_START==="
    end_delim = f"==={tag_name}_END==="

    if start_delim in content and end_delim in content:
        return content.split(start_delim)[1].split(end_delim)[0].strip()

    return content.strip()


def generate_recognition_assets(raw_payload: str) -> str:
    """Executes prompt against model cascade with disabled automatic function calling warnings."""
    prompt = RECOGNITION_EVENT_PROMPT.format(raw_data_payload=raw_payload)

    def _api_func_builder(target_model: str):
        def _api_call():
            print(f"Generating Recognition Event assets using model: {target_model}")

            # Suppress SDK warning logs
            gen_config = types.GenerateContentConfig(
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

    return call_with_fallback(_api_func_builder)


def git_commit_assets(saved_paths: list[Path]) -> None:
    """Commits created distribution assets to local Git tracking."""
    if not saved_paths:
        return

    try:
        rel_paths = [
            str(p.relative_to(PROJECT_ROOT)) for p in saved_paths
        ]
        subprocess.run(["git", "add"] + rel_paths, check=True)
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"Stage & transform research assets into {len(saved_paths)} distribution files",
            ],
            check=True,
        )
        print(f"[Git] Successfully committed {len(saved_paths)} asset file(s)")
    except Exception as e:
        print(f"[Git Warning] Automated commit skipped: {e}")


def process_latest_research():
    print("Starting Stage & Transform Engine...")

    # 1. Resolve research payload path
    if RESEARCH_PRIMARY_PATH.exists():
        research_path = RESEARCH_PRIMARY_PATH
    elif RESEARCH_FALLBACK_PATH.exists():
        research_path = RESEARCH_FALLBACK_PATH
    else:
        raise FileNotFoundError(
            f"latest_research.md not found in '{RESEARCH_PRIMARY_PATH}' or '{RESEARCH_FALLBACK_PATH}'."
        )

    print(
        f"Loading raw research payload from: {research_path.relative_to(PROJECT_ROOT)}"
    )
    raw_payload = research_path.read_text(encoding="utf-8")

    # 2. Generate content via central config.py model cascade
    content = generate_recognition_assets(raw_payload)

    # 3. Extract target sections
    threads_content = extract_section(content, "THREADS")
    substack_content = extract_section(content, "SUBSTACK")
    blogger_content = extract_section(content, "BLOGGER")

    # 4. UTC timestamp matching system standards
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")

    targets = [
        (
            DISTRIBUTION_DIR / "Threads",
            f"{timestamp}_threads_draft.md",
            "latest_threads.md",
            threads_content,
        ),
        (
            DISTRIBUTION_DIR / "Substack",
            f"{timestamp}_substack_draft.md",
            "latest_substack.md",
            substack_content,
        ),
        (
            DISTRIBUTION_DIR / "Blogger",
            f"{timestamp}_blogger_draft.md",
            "latest_blogger.md",
            blogger_content,
        ),
    ]

    saved_paths: list[Path] = []

    # 5. Save archive and pointer files
    for folder_path, timestamped_filename, latest_filename, body in targets:
        folder_path.mkdir(parents=True, exist_ok=True)

        archive_file = folder_path / timestamped_filename
        archive_file.write_text(body, encoding="utf-8")
        saved_paths.append(archive_file)
        print(f"[+] Archived asset: {archive_file.relative_to(PROJECT_ROOT)}")

        latest_file = folder_path / latest_filename
        latest_file.write_text(body, encoding="utf-8")
        saved_paths.append(latest_file)
        print(f"[+] Updated pointer: {latest_file.relative_to(PROJECT_ROOT)}")

    # 6. Auto-commit output files
    git_commit_assets(saved_paths)


if __name__ == "__main__":
    process_latest_research()
