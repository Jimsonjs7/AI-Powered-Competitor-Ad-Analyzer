from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text
from app.core.database import Base


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    rows_collected = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
