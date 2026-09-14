import os
import json
import glob
from datetime import datetime, timezone
from google import genai
from google.genai import types

# System path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAPTURE_DIR = os.path.join(BASE_DIR, "capture", "raw_notes")
MEMORY_VAULT_DIR = os.path.join(BASE_DIR, "MemoryVault")

DASHBOARD_FEED_PATH = os.path.join(MEMORY_VAULT_DIR, "dashboard_feed.json")
IP_VAULT_PATH = os.path.join(MEMORY_VAULT_DIR, "ip_vault.json")

# Initialize Gemini Client (Uses GEMINI_API_KEY environment variable)
client = genai.Client()

SYSTEM_INSTRUCTION = """
You are the Sovereign Content Engine—a zero-fluff, high-signal media mutation system.
Your job is to take a raw, unrefined thought/signal and mutate it into a high-leverage content asset.

Produce your response in STRICT JSON matching this exact structure:
{
  "title": "A crisp, authoritative title for this asset",
  "axiom": "The foundational underlying truth or framework concept extracted from this raw seed in 1 sharp sentence.",
  "domain": "The operational domain (e.g., Sovereign Mindset, System Design, Execution, IP Strategy)",
  "mutations": {
    "substack_note": "A sharp, punchy Substack Note (~2-4 sentences max). Zero fluff, pure punch.",
    "x_post": "A concise post optimized for high-signal engagement on X.",
    "linkedin_asset": "A structured, authoritative insight post tailored for LinkedIn.",
    "framework_breakdown": "A bulleted breakdown of the core underlying framework."
  }
}
"""

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return [] if "vault" in filepath else {}
    return [] if "vault" in filepath else {}

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def process_raw_seeds():
    # Gather all txt and md files from capture/raw_notes/
    raw_files = glob.glob(os.path.join(CAPTURE_DIR, "*.txt")) + glob.glob(os.path.join(CAPTURE_DIR, "*.md"))
    
    if not raw_files:
        print("No raw seeds found in capture/raw_notes/. Engine idle.")
        return

    dashboard_feed = load_json(DASHBOARD_FEED_PATH)
    ip_vault = load_json(IP_VAULT_PATH)

    if "pending_dispatches" not in dashboard_feed:
        dashboard_feed["pending_dispatches"] = []

    for file_path in raw_files:
        filename = os.path.basename(file_path)
        print(f"Processing raw seed: {filename}...")

        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read().strip()

        if not raw_content:
            os.remove(file_path)
            continue

        # Call Gemini 2.5 Flash for rapid, structured mutation
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=f"Mutate this raw seed:\n\n{raw_content}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                temperature=0.3
            )
        )

        try:
            mutated_data = json.loads(response.text)
            seed_id = f"seed_{int(datetime.now(timezone.utc).timestamp())}"
            timestamp = datetime.now(timezone.utc).isoformat()

            # 1. Store Mutated Dispatch for CommandHub
            dispatch_item = {
                "id": seed_id,
                "processed_at": timestamp,
                "title": mutated_data.get("title", "Untitled Signal"),
                "domain": mutated_data.get("domain", "General"),
                "mutations": mutated_data.get("mutations", {}),
                "source_file": filename
            }
            dashboard_feed["pending_dispatches"].insert(0, dispatch_item)

            # 2. Extract & Persist Core Axiom into ip_vault.json
            axiom_text = mutated_data.get("axiom")
            if axiom_text:
                ip_item = {
                    "id": f"ip_{int(datetime.now(timezone.utc).timestamp())}",
                    "axiom": axiom_text,
                    "domain": mutated_data.get("domain", "General"),
                    "source_seed": seed_id,
                    "created_at": timestamp,
                    "times_mutated": 1
                }
                ip_vault.insert(0, ip_item)

            # Cleanup ingested seed file to keep capture/ clean
            os.remove(file_path)
            print(f"Successfully mutated {filename} into pending dispatches.")

        except json.JSONDecodeError:
            print(f"Error parsing Gemini response for {filename}. Raw output logged.")

    # Update state files
    dashboard_feed["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_json(DASHBOARD_FEED_PATH, dashboard_feed)
    save_json(IP_VAULT_PATH, ip_vault)
    print("Engine processing complete. MemoryVault updated.")

if __name__ == "__main__":
    process_raw_seeds()
