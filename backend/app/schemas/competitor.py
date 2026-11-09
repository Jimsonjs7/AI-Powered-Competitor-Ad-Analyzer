from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    needs_review = "needs_review"


class CompetitorCreate(BaseModel):
    name: str = Field(..., max_length=200, description="Institute brand name")
    city: str = Field(default="Coimbatore", max_length=100)
    course: str = Field(default="AI", max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    fb_page_id: Optional[str] = Field(None, max_length=100)
    fb_page_url: Optional[str] = Field(None, max_length=500)


class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    course: Optional[str] = None
    website: Optional[str] = None
    fb_page_id: Optional[str] = None
    confidence: Optional[ConfidenceLevel] = None
    is_active: Optional[bool] = None


class CompetitorResponse(BaseModel):
    id: int
    name: str
    city: str
    course: str
    website: Optional[str]
    fb_page_id: Optional[str]
    confidence: ConfidenceLevel
    active_ads_count: int = 0
    is_active: bool = True
    created_at: datetime
