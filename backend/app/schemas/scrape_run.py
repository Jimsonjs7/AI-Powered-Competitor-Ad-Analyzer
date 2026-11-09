from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ScrapeRunRecord(BaseModel):
    id: int
    provider: str
    status: str
    rows_collected: int
    duration_ms: int
    error_message: Optional[str] = None
    created_at: datetime


class HealthStatusResponse(BaseModel):
    status: str
    active_providers_count: int
    total_providers_count: int
    message: str
    providers_health: dict
