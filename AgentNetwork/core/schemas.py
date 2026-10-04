from pydantic import BaseModel, Field
from typing import List, Optional

class SignalPayload(BaseModel):
    signal_id: str = Field(..., description="Unique hash for deduplication tracking")
    demand_type: str = Field(..., description="evergreen_utility | real_time_intent")
    universal_pain_point: str = Field(..., description="Core human friction (e.g. lost time, context switching)")
    search_query: str = Field(..., description="The query string or seed used")
    target_hook: str = Field(..., description="0-3s pattern-break opening line")
    actionable_takeaway: str = Field(..., description="Clear 1-step resolution")
    content_pillar: str = Field(..., description="mindset | execution | systems")
    visual_keywords: List[str] = Field(..., description="Visual search terms for Pexels background rendering")

class ScriptPayload(BaseModel):
    title: str = Field(..., description="Internal reference title")
    hook_text: str = Field(..., description="On-screen text hook for 0-3s mark")
    voiceover_script: str = Field(..., description="Full spoken script for TTS engine")
    body_points: List[str] = Field(..., description="Bullet points for visual text overlays")
    call_to_action: str = Field(..., description="Ending engagement prompt")
    theme: str = Field(..., description="sovereign | ambient | kinetic")
    visual_search_queries: List[str] = Field(..., description="Keywords for MoviePy asset fetching")

class ExecutionConfig(BaseModel):
    mode: str = Field("single", description="single | batch")
    batch_size: int = Field(1, description="Number of assets to generate in batch mode")
    force_evergreen: bool = Field(False, description="Override and force evergreen seed pool")
