import os
import json

class SovereignStrategist:
    """Agent 1: Specialized in high-friction psychological hooks, human drive, and relentless discipline."""

    SYSTEM_PROMPT = """You are The Sovereign Strategist. Your sole directive is to reverse-engineer human attention, friction, and drive for Instagram Reels.
    
    CORE PRINCIPLES:
    - Target deep cognitive friction: fear of stagnation, wasted potential, cheap dopamine traps, and soft habits.
    - Output raw, uncompromising truth. Zero generic motivational fluff.
    - Leverage psychological triggers: Status anxiety, pattern interrupts, ruthless self-reliance, and extreme focus.
    
    Return a structured JSON payload with:
    {
      "core_friction": "The exact mental trap or habit being exposed",
      "hook": "Unapologetic 1-sentence scroll-stopper (under 10 words)",
      "narrative_arc": [
        "Point 1: Expose the weak standard/trap",
        "Point 2: Reframe the reality with cold logic",
        "Point 3: The non-negotiable protocol/action"
      ],
      "b_roll_theme": "High-contrast dark moody aesthetic keywords for stock footage"
    }
    """

    def generate_strategy(self, friction_signal: str) -> dict:
        api_key = os.getenv("GEMINI_API_KEY")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=self.SYSTEM_PROMPT)
            prompt = f"Analyze and generate a psychological script architecture for this input friction: '{friction_signal}'"
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[!] SovereignStrategist warning: {e}. Executing standard fallback payload.")
            return {
                "core_friction": friction_signal,
                "hook": "Stop wasting potential on cheap comfort.",
                "narrative_arc": [
                    "Comfort kills ambition faster than failure.",
                    "Build systems that operate independent of emotions.",
                    "Execute the daily non-negotiables without debate."
                ],
                "b_roll_theme": "dark minimalist high-contrast motion"
            }


class KineticScriptwright:
    """Agent 2: Converts raw psychological strategy into scene-by-scene timing and B-roll directives for MediaFactory."""

    SYSTEM_PROMPT = """You are The Kinetic Scriptwright. You transform raw mindset strategy into frame-level 9:16 visual blueprints.
    
    RULES:
    - Keep dynamic line wrapping short and impactful.
    - Scene duration must be fast-paced (2 to 4 seconds per scene max).
    - Map precise, dark-aesthetic B-roll queries for Pexels search (e.g. 'dark moody traffic', 'focused night coding', 'street lights motion').
    
    Return a structured JSON payload ready for MediaFactory:
    {
      "title": "Clean_File_Name_Title",
      "caption": "Full Instagram caption text including ruthless CTA and hashtags.",
      "scenes": [
        {
          "scene_index": 0,
          "text": "ON-SCREEN TEXT OVERLAY",
          "query": "dark minimalist tech code night",
          "duration": 3.0
        }
      ]
    }
    """

    def compile_blueprint(self, strategy_data: dict) -> dict:
        api_key = os.getenv("GEMINI_API_KEY")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=self.SYSTEM_PROMPT)
            prompt = f"Compile this strategy into an optimized script blueprint:\n{json.dumps(strategy_data)}"
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[!] KineticScriptwright warning: {e}. Executing standard fallback payload.")
            hook = strategy_data.get("hook", "Stop Doing Manual Work")
            clean_title = hook.lower().replace(" ", "_").replace("'", "").replace(".", "")[:30]
            return {
                "title": clean_title,
                "caption": f"{hook}\n\nExecution over speculation. Systemize the workflow.\n\n#automation #productivity #systems #operator",
                "scenes": [
                    {
                        "scene_index": 0,
                        "text": hook,
                        "query": "dark moody minimalist office screen",
                        "duration": 3.0
                    },
                    {
                        "scene_index": 1,
                        "text": "Comfort is the hidden killer of progress.",
                        "query": "night city street lights blur motion",
                        "duration": 3.5
                    },
                    {
                        "scene_index": 2,
                        "text": "Build systems that execute without feelings.",
                        "query": "focused person typing code dark room",
                        "duration": 3.0
                    }
                ]
            }
