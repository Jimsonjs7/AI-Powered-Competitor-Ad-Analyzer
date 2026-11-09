from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False)
    ad_id = Column(Integer, ForeignKey("ads.id", ondelete="SET NULL"), nullable=True)
    source = Column(String(100), nullable=False)
    text_hash = Column(String(64), nullable=False, index=True)
    text = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)
    sentiment = Column(String(20), nullable=True)
    category = Column(String(100), nullable=True)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    expires_at = Column(DateTime, nullable=True)

    competitor = relationship("Competitor")
    ad = relationship("Ad")

