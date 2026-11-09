from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DiscoveryRunRequest(BaseModel):
    radius_km: float = Field(default=10.0, ge=1.0, le=100.0)
    search_terms: Optional[List[str]] = None


class DiscoveryRunResponse(BaseModel):
    run_id: int
    status: str
    message: str


class DiscoveryStatusResponse(BaseModel):
    run_id: int
    status: str
    current_step: Optional[str] = None
    radius_km: float
    filters: Dict[str, Any] = Field(default_factory=dict)
    counts: Dict[str, int] = Field(default_factory=dict)
    cost_usd: float = 0.0
    started_at: datetime
    finished_at: Optional[datetime] = None

