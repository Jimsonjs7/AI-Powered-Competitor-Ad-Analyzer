from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    city = Column(String(100), default="Coimbatore", index=True)
    course = Column(String(100), default="AI")
    website = Column(String(500), nullable=True)
    fb_page_id = Column(String(100), nullable=True, index=True)
    confidence = Column(String(50), default="high")
    is_active = Column(Boolean, default=True)

    # v2 extensions: location & discovery
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    distance_km = Column(Float, nullable=True)
    area = Column(String(200), nullable=True)
    ig_handle = Column(String(100), nullable=True)
    data_status = Column(String(50), default="pending")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    ads = relationship("Ad", back_populates="competitor", cascade="all, delete-orphan")
    metrics = relationship("CompetitorMetrics", back_populates="competitor", uselist=False, cascade="all, delete-orphan")
