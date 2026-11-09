from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MediaItem(BaseModel):
    type: str = Field(..., description="Media type: image or video")
    url: str = Field(..., description="Original platform CDN media URL")
    storage_path: Optional[str] = Field(None, description="Local or object storage path")
    hash: Optional[str] = Field(None, description="Content SHA256 hash")


class AdRecord(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    ad_archive_id: str = Field(..., description="Unique ad archive identifier across providers")
    page_id: str = Field(..., description="Facebook Page ID")
    page_name: str = Field(..., description="Competitor institute name")
    source: str = Field(..., description="Data provider: apify, scrapecreators, playwright, manual")
    copy: str = Field("", description="Primary ad copy text")
    headline: Optional[str] = Field(None, description="Ad card headline")
    cta: Optional[str] = Field(None, description="Call to action button label")
    platforms: List[str] = Field(default_factory=lambda: ["facebook", "instagram"])
    start_date: Optional[str] = Field(None, description="First date ad started running")
    is_active: bool = Field(True, description="Whether the ad is actively running")
    media: List[MediaItem] = Field(default_factory=list)
    language: Optional[str] = Field(None, description="Detected ad language")
    raw: Optional[Any] = Field(None, description="Original raw provider response for audit")


class AdResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    id: int
    ad_archive_id: str
    competitor_id: int
    competitor_name: str
    course: str
    copy: str
    headline: Optional[str]
    cta: Optional[str]
    platforms: List[str]
    start_date: Optional[str]
    is_active: bool
    first_seen: datetime
    last_seen: datetime
    run_days: int
    media_url: Optional[str]
    media_type: Optional[str]
    score: Optional[int] = None
    hook: Optional[str] = None
    offer: Optional[str] = None
    audience: Optional[str] = None
    tactics: List[str] = Field(default_factory=list)
    why: Optional[str] = None
    weak: Optional[str] = None
    created_at: datetime


class AdFilterParams(BaseModel):
    competitor_ids: Optional[List[int]] = None
    course: Optional[str] = None
    city: Optional[str] = "Coimbatore"
    sort_by: str = "days"
    limit: int = 100
    offset: int = 0


class MarketInsightResponse(BaseModel):
    headline: str
    subline: str
    top_hook: str
    hook_percentage: int
    course_distribution: Dict[str, int]
    gap_course: str
    total_active_ads: int
