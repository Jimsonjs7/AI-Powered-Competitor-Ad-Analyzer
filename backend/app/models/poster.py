from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.core.database import Base


class Poster(Base):
    __tablename__ = "posters"

    id = Column(Integer, primary_key=True, index=True)
    source_ad_id = Column(Integer, ForeignKey("ads.id", ondelete="SET NULL"), nullable=True)
    course = Column(String(100), default="AI")
    angle_name = Column(String(50), default="Outcome")
    size_format = Column(String(50), default="feed")
    headline = Column(String(200), nullable=False)
    subline = Column(String(300), nullable=False)
    cta_text = Column(String(100), default="Book a free demo")
    prompt = Column(Text, nullable=False)
    image_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
