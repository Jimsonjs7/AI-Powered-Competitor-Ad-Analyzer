from typing import List, Optional
from pydantic import BaseModel, Field


class VisualStyle(BaseModel):
    palette: List[str] = Field(default_factory=list, description="Extracted hex color codes")
    layout: str = Field("", description="Visual composition type")
    typography: str = Field("", description="Font weights and sizing notes")


class AdAnalysisSchema(BaseModel):
    course: str = Field(..., description="Target course subject")
    hook: str = Field(..., description="Core attention hook")
    offer: str = Field(..., description="Specific offer promise or price anchor")
    cta: str = Field(..., description="Call to action phrasing")
    target_audience: str = Field(..., description="Target persona description")
    emotional_triggers: List[str] = Field(default_factory=list)
    persuasion_tactics: List[str] = Field(default_factory=list)
    visual_style: VisualStyle = Field(default_factory=VisualStyle)
    why_it_works: str = Field(..., description="Strategic analysis of effectiveness")
    weaknesses: str = Field(..., description="Flaws or missing proof points")
    effectiveness_score: int = Field(..., ge=0, le=100, description="Overall score out of 100")
    brandmonk_opportunity: str = Field(..., description="Specific angle BrandMonk can capitalize on")


class AnalysisResponse(BaseModel):
    id: int
    ad_id: int
    analysis: AdAnalysisSchema
    cached: bool = True

