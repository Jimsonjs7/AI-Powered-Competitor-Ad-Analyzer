from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class AdMedia(Base):
    __tablename__ = "ad_media"

    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ads.id", ondelete="CASCADE"), nullable=False)
    media_type = Column(String(50), default="image")
    original_url = Column(String(1000), nullable=False)
    storage_path = Column(String(500), nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    ad = relationship("Ad", back_populates="media")
