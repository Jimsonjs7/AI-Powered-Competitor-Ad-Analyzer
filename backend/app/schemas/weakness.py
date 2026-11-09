from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class WeaknessResponse(BaseModel):
    id: int
    competitor_id: int
    category: str
    summary: str
    evidence_count: int
    sample_size: int
    share_percent: float
    confidence: str
    severity: int
    computed_at: datetime


class DataSufficiencyResponse(BaseModel):
    competitor_id: int
    ads_count: int
    reviews_count: int
    comments_count: int
    is_sufficient: bool
    missing: List[str]


class WeaknessListResponse(BaseModel):
    competitor_id: int
    weaknesses: List[WeaknessResponse]
    data_status: str
    total_evidence: int
    is_sufficient: bool
    analyzed_at: Optional[datetime] = None

