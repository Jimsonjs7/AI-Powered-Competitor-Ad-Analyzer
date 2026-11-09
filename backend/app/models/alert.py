from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # new_ad, dropped_ad, price_change, long_running
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data_json = Column(Text, default="{}")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    competitor = relationship("Competitor")

