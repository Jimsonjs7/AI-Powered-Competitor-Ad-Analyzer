from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class AdAnalysis(Base):
    __tablename__ = "ad_analysis"

    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ads.id", ondelete="CASCADE"), unique=True, nullable=False)
    effectiveness_score = Column(Integer, default=70)
    hook = Column(String(500), nullable=False)
    offer = Column(String(500), nullable=False)
    target_audience = Column(String(500), nullable=False)
    tactics_str = Column(String(500), default="")
    emotional_triggers_str = Column(String(500), default="")
    why_it_works = Column(Text, nullable=False)
    weaknesses = Column(Text, nullable=False)
    brandmonk_opportunity = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=True)
    model_name = Column(String(100), default="gemini-2.5-flash")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    ad = relationship("Ad", back_populates="analysis")
