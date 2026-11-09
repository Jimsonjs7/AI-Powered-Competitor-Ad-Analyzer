from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    ad_archive_id = Column(String(120), unique=True, index=True, nullable=False)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(50), nullable=False)
    copy = Column(Text, default="")
    headline = Column(String(300), nullable=True)
    cta = Column(String(100), nullable=True)
    platforms_str = Column(String(200), default="facebook,instagram")
    start_date = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)

    # Persistence tracking fields
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    run_days = Column(Integer, default=1)

    raw_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    competitor = relationship("Competitor", back_populates="ads")
    media = relationship("AdMedia", back_populates="ad", cascade="all, delete-orphan")
    analysis = relationship("AdAnalysis", back_populates="ad", uselist=False, cascade="all, delete-orphan")
