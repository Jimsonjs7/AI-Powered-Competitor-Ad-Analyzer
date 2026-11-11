from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CompetitorAdFlawAudit(BaseModel):
    competitor_name: str
    headline: Optional[str] = None
    copy_snippet: str
    active_days: int
    detected_hook: str
    detected_offer: str
    vulnerabilities: List[str]
    creative_fatigue_level: str
    unaddressed_prospect_doubts: List[str]


class CounterCreativeAngle(BaseModel):
    angle_type: str
    angle_name: str
    strategic_rationale: str
    target_flaw_in_competitor: str
    matching_approved_claim: str
    hook: str
    headline: str
    subline: str
    primary_text: str
    cta_text: str
    urgency_tagline: Optional[str] = None
    visual_concept: str
    composition: str
    color_palette: List[str] = Field(
        default_factory=lambda: ["#0A7C6E", "#111827", "#F6F7F5", "#FFFFFF"]
    )
    typography_guide: str
    aspect_ratios: Dict[str, str] = Field(default_factory=dict)
    image_prompt: str
    negative_prompt: str = "text, lettering, watermark, blurry, deformed, low quality, stock watermark"


class CreativeCounterAdResponse(BaseModel):
    ad_id: int
    client_name: str
    course: str
    competitor_audit: CompetitorAdFlawAudit
    angles: List[CounterCreativeAngle]
    recommended_cta: str
    created_at: datetime

