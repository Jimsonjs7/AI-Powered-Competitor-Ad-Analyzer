from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    needs_review = "needs_review"


class CompetitorMetricsResponse(BaseModel):
    active_ads: int = 0
    new_this_week: int = 0
    longest_run_days: int = 0
    rating: Optional[float] = None
    review_count: int = 0
    negative_share: float = 0.0
    comment_count: int = 0
    weakness_score: float = 0.0
    threat_score: float = 0.0
    computed_at: Optional[datetime] = None


class CompetitorCreate(BaseModel):
    name: str = Field(..., max_length=200, description="Institute brand name")
    city: str = Field(default="Coimbatore", max_length=100)
    course: str = Field(default="AI", max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    fb_page_id: Optional[str] = Field(None, max_length=100)
    fb_page_url: Optional[str] = Field(None, max_length=500)
    lat: Optional[float] = None
    lng: Optional[float] = None
    distance_km: Optional[float] = None
    area: Optional[str] = None
    ig_handle: Optional[str] = None


class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    course: Optional[str] = None
    website: Optional[str] = None
    fb_page_id: Optional[str] = None
    confidence: Optional[ConfidenceLevel] = None
    is_active: Optional[bool] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    distance_km: Optional[float] = None
    area: Optional[str] = None
    ig_handle: Optional[str] = None
    data_status: Optional[str] = None


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
    lat: Optional[float] = None
    lng: Optional[float] = None
    distance_km: Optional[float] = None
    area: Optional[str] = None
    ig_handle: Optional[str] = None
    data_status: str = "pending"
    metrics: Optional[CompetitorMetricsResponse] = None
    created_at: datetime


class CompetitorDiscoverRequest(BaseModel):
    city: str = Field(default="Coimbatore", description="City to search competitors in")
    query: Optional[str] = Field(None, description="Search keyword, e.g. AI course, UI UX institute")
    limit: int = Field(default=10, ge=1, le=50)


class CompetitorDiscoverItem(BaseModel):
    name: str
    city: str
    course: str
    website: Optional[str] = None
    suggested_page_id: Optional[str] = None
    confidence: ConfidenceLevel


class PageResolveRequest(BaseModel):
    input_text: str = Field(..., description="Institute name, website URL, or Facebook Page URL")


class PageResolveResponse(BaseModel):
    resolved_name: str
    resolved_page_id: Optional[str]
    confidence: ConfidenceLevel
    source: str
