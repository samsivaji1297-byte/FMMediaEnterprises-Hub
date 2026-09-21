import os
import sys
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY missing.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

print("Testing Gemini Live Google Search Grounding...")

config = types.GenerateContentConfig(
    tools=[types.Tool(google_search=types.GoogleSearch())]
)

chat = client.chats.create(model="gemini-3.6-flash", config=config)
response = chat.send_message("What are 3 trending topics in AI automation this week? Keep it brief.")

print("\n--- RESPONSE ---")
print(response.text)

# Inspect search queries executed by Gemini
try:
    metadata = response.candidates[0].grounding_metadata
    if metadata and getattr(metadata, 'web_search_queries', None):
        print("\n--- SEARCH QUERIES EXECUTED BY GEMINI ---")
        for q in metadata.web_search_queries:
            print(f"- {q}")
except Exception as e:
    print(f"\nCould not extract search metadata: {e}")test_search.py
