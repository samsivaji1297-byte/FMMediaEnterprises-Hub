import os
import json
from pathlib import Path
from AgentNetwork.core.schemas import ScriptPayload, SignalPayload

class ScriptEngineAgent:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    def generate_script(self, signal: SignalPayload) -> ScriptPayload:
        print(f"[*] Generating high-friction conversion script for signal: {signal.signal_id}")

        aggressive_hooks = [
            f"You are burning 20 hours a week doing manual work.",
            f"Stop trading manual hours for broken scale.",
            f"Manual execution is killing your business leverage.",
            f"If your business relies on manual tasks, it is broken."
        ]
        
        import random
        selected_hook = random.choice(aggressive_hooks)

        voiceover = (
            f"{selected_hook} Most operators stay trapped in low-leverage execution. "
            f"High-yield systems deploy automated infrastructure to route leads, execute delivery, "
            f"and scale without human bottlenecks. Reclaim sovereign control over your time. "
            f"Comment OPERATOR below to deploy the full system."
        )

        return ScriptPayload(
            script_id=f"script_{signal.signal_id}",
            title="Sovereign Infrastructure Execution",
            hook_text=selected_hook,
            body_points=[
                "Deploy automated workflows",
                "Eliminate manual bottlenecks",
                "Scale sovereign infrastructure"
            ],
            voiceover_script=voiceover,
            call_to_action="Comment OPERATOR to deploy the automated architecture.",
            theme="sovereign",
            visual_search_queries=[
                "cyberpunk dark terminal",
                "abstract glowing grid loop",
                "futuristic dark server infrastructure"
            ]
        )
