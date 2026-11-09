from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ObjectionClusterResponse(BaseModel):
    id: int
    label: str
    category: str
    total_count: int
    competitor_count: int
    intensity: float
    created_at: datetime


class OpportunityResponse(BaseModel):
    id: int
    cluster_id: int
    cluster_label: str
    category: str
    score: float
    counter_angle: Optional[str]
    formats: List[str]
    headlines: List[str]
    primary_text: Optional[str]
    missing_proof: List[str]
    status: str
    created_at: datetime


class OpportunityDraftRequest(BaseModel):
    opportunity_id: int
    approved_claims_only: bool = True


class OpportunityDraftResponse(BaseModel):
    opportunity_id: int
    headline_options: List[str]
    primary_text: str
    cta: str
    recommended_format: str
    used_claims: List[str]
    missing_claims: List[str]
    compliance_note: str

