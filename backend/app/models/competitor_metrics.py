from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


class CompetitorMetrics(Base):
    __tablename__ = "competitor_metrics"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), unique=True, nullable=False)
    active_ads = Column(Integer, default=0)
    new_this_week = Column(Integer, default=0)
    longest_run_days = Column(Integer, default=0)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, default=0)
    negative_share = Column(Float, default=0.0)
    comment_count = Column(Integer, default=0)
    weakness_score = Column(Float, default=0.0)
    threat_score = Column(Float, default=0.0)
    computed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    competitor = relationship("Competitor", back_populates="metrics")

