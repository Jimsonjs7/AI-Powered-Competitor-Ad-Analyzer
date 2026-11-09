from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceImportRequest(BaseModel):
    competitor_id: int
    source: str = Field(default="manual", description="google_maps, fb_comments, manual, website_gap, ad_copy_gap")
    text: str = Field(..., max_length=2000, description="Comment or review content (untrusted)")
    category: Optional[str] = None
    ad_id: Optional[int] = None


class EvidenceItemResponse(BaseModel):
    id: int
    competitor_id: int
    ad_id: Optional[int] = None
    source: str
    text: str
    language: Optional[str] = None
    sentiment: Optional[str] = None
    category: Optional[str] = None
    collected_at: datetime


class EvidenceListResponse(BaseModel):
    competitor_id: int
    items: List[EvidenceItemResponse]
    total: int
    source_breakdown: Dict[str, int]

