import os
import random
from pathlib import Path
from AgentNetwork.core.schemas import ScriptPayload, SignalPayload

class ScriptEngineAgent:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    def generate_script(self, signal: SignalPayload) -> ScriptPayload:
        print(f"[*] Generating The Compression System monetization script for signal: {signal.signal_id}")

        # High-converting disruption hooks centered around audience myths and digital product leverage
        compression_hooks = [
            "YOU DON'T NEED AN AUDIENCE TO SELL DIGITAL PRODUCTS.",
            "STOP WAITING FOR THOUSANDS OF FOLLOWERS TO START.",
            "BUILD YOUR FIRST DIGITAL PRODUCT THIS WEEKEND.",
            "ONE PROBLEM. ONE SOLUTION. ONE PAYMENT LINK."
        ]
        
        selected_hook = random.choice(compression_hooks)

        voiceover = (
            f"{selected_hook} You don't need a team, a warehouse, or a complicated business. "
            f"Find one problem someone already wants solved, use AI to turn the solution into a digital product, "
            f"and put it where buyers can find it. Build your first version this weekend. "
            f"Get the full system at fmframeworks.gumroad.com/l/CompressionSystem."
        )

        return ScriptPayload(
            script_id=f"script_{signal.signal_id}",
            title="The Compression System",
            hook_text=selected_hook,
            body_points=[
                "Find one real problem",
                "Use AI to build the solution",
                "Launch your digital product"
            ],
            voiceover_script=voiceover,
            call_to_action="Get The Compression System: fmframeworks.gumroad.com/l/CompressionSystem",
            theme="sovereign",
            visual_search_queries=[
                "digital product architecture matrix",
                "cyberpunk terminal glowing code",
                "minimalist dark financial grid"
            ]
        )
