from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class ObjectionCluster(Base):
    __tablename__ = "objection_clusters"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(300), nullable=False)
    category = Column(String(100), nullable=False)
    total_count = Column(Integer, default=0)
    competitor_count = Column(Integer, default=0)
    intensity = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    opportunities = relationship("Opportunity", back_populates="cluster", cascade="all, delete-orphan")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("objection_clusters.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, default=0.0)
    counter_angle = Column(Text, nullable=True)
    formats_json = Column(Text, default="[]")
    headlines_json = Column(Text, default="[]")
    primary_text = Column(Text, nullable=True)
    missing_proof_json = Column(Text, default="[]")
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    cluster = relationship("ObjectionCluster", back_populates="opportunities")

