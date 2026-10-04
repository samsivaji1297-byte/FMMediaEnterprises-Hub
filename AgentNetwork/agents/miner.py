import json
import random
import hashlib
from typing import List
from duckduckgo_search import DDGS  # Free keyless web search
from config import get_client, call_with_fallback
from google.genai import types
from AgentNetwork.core.schemas import SignalPayload, ExecutionConfig
from AgentNetwork.config.settings import SEEDS_FILE, QUEUE_FILE

class SignalMinerAgent:
    def __init__(self):
        self.client = get_client()
        with open(SEEDS_FILE, 'r') as f:
            self.seeds = json.load(f)["evergreen_pillars"]

    def _get_live_duckduckgo_signals(self, topic: str) -> str:
        """Fetches live search intent snippets via DuckDuckGo."""
        results = []
        try:
            with DDGS() as ddgs:
                # Pull top 3 search intent results
                for r in ddgs.text(topic, max_results=3):
                    results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}")
        except Exception as e:
            print(f"[!] DuckDuckGo search fallback: {e}")
            results.append("Live search unavailable. Relying on baseline demand model.")
        return "\n---\n".join(results)

    def extract_signals(self, config: ExecutionConfig) -> List[SignalPayload]:
        """Generates validated SignalPayload objects (Single or Batch)."""
        signals = []
        count = config.batch_size if config.mode == "batch" else 1

        for _ in range(count):
            # Select demand source: Evergreen vs Real-Time
            use_evergreen = config.force_evergreen or (random.random() < 0.5)
            category = random.choice(list(self.seeds.keys()))
            seed_query = random.choice(self.seeds[category])

            if use_evergreen:
                demand_type = "evergreen_utility"
                context = f"Evergreen High-Utility Demand Seed: {seed_query}"
            else:
                demand_type = "real_time_intent"
                live_data = self._get_live_duckduckgo_signals(seed_query)
                context = f"Live Market Query: {seed_query}\nRecent Search Signals:\n{live_data}"

            # Gemini Prompting via call_with_fallback
            prompt = f"""
            You are a Demand Mining Agent specializing in high-converting, short-form content.
            Analyze this input and construct a high-retention video signal.

            INPUT CONTEXT:
            {context}

            REQUIREMENTS:
            1. Identify the universal human friction (lost time, cognitive overload, manual drag).
            2. Craft a 0-3s pattern-break text hook targeting this exact pain point.
            3. Provide a crisp 1-step resolution.
            4. Suggest 2 stock video search keywords for background visuals.

            Return JSON matching this schema:
            {{
                "universal_pain_point": "str",
                "search_query": "{seed_query}",
                "target_hook": "str",
                "actionable_takeaway": "str",
                "content_pillar": "mindset|execution|systems",
                "visual_keywords": ["str", "str"]
            }}
            """

            def api_call(model_name: str):
                res = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                return res.text

            raw_json = call_with_fallback(api_call)
            data = json.loads(raw_json)

            # Generate unique hash ID
            sig_hash = hashlib.md5(f"{seed_query}_{data['target_hook']}".encode()).hexdigest()[:10]

            payload = SignalPayload(
                signal_id=f"sig_{sig_hash}",
                demand_type=demand_type,
                universal_pain_point=data["universal_pain_point"],
                search_query=seed_query,
                target_hook=data["target_hook"],
                actionable_takeaway=data["actionable_takeaway"],
                content_pillar=data["content_pillar"],
                visual_keywords=data["visual_keywords"]
            )
            signals.append(payload)

        return signals
