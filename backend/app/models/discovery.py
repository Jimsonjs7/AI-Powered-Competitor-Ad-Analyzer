from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from app.core.database import Base


class DiscoveryRun(Base):
    __tablename__ = "discovery_runs"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("business_profiles.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="pending")
    current_step = Column(String(200), nullable=True)
    radius_km = Column(Float, default=10.0)
    filters_json = Column(Text, default="{}")
    providers_json = Column(Text, default="[]")
    counts_json = Column(Text, default="{}")
    cost_usd = Column(Float, default=0.0)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    finished_at = Column(DateTime, nullable=True)

