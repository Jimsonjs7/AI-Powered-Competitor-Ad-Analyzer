from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Weakness(Base):
    __tablename__ = "weaknesses"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    evidence_count = Column(Integer, default=0)
    sample_size = Column(Integer, default=0)
    share_percent = Column(Float, default=0.0)
    confidence = Column(String(20), default="medium")
    severity = Column(Integer, default=1)
    computed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    competitor = relationship("Competitor")

