from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    competitor_id: int
    competitor_name: str
    alert_type: str
    title: str
    message: str
    data: Dict[str, Any]
    is_read: bool
    created_at: datetime


class WeeklyDigestResponse(BaseModel):
    generated_at: datetime
    active_competitors_count: int
    total_active_ads: int
    new_ads_this_week: int
    unread_alerts_count: int
    top_rising_objections: List[Dict[str, Any]]
    top_opportunities: List[Dict[str, Any]]
    summary: str

