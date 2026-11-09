from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(Integer, default=1)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    tagline = Column(String(300), nullable=True)
    business_type_json = Column(Text, default="[]")
    domains_json = Column(Text, default="[]")
    city = Column(String(100), default="Coimbatore")
    area = Column(String(200), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    radius_km = Column(Float, default=10.0)
    website = Column(String(500), nullable=True)
    tone = Column(String(200), default="Professional and outcome-focused")
    target_audience = Column(String(300), nullable=True)
    price_positioning = Column(String(50), default="mid")
    languages_json = Column(Text, default='["English"]')
    primary_goal = Column(String(200), default="enquiries")
    monthly_budget_range = Column(String(100), nullable=True)
    preferred_cta = Column(String(200), default="Book a free demo")
    thresholds_json = Column(Text, default='{"min_ads": 3, "min_reviews": 20, "min_comments": 15}')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    services = relationship("ProfileService", back_populates="profile", cascade="all, delete-orphan")
    claims = relationship("ProfileClaim", back_populates="profile", cascade="all, delete-orphan")
    social_accounts = relationship("ProfileSocialAccount", back_populates="profile", cascade="all, delete-orphan")


class ProfileService(Base):
    __tablename__ = "profile_services"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    fee_min = Column(Float, nullable=True)
    fee_max = Column(Float, nullable=True)
    duration = Column(String(100), nullable=True)
    mode = Column(String(50), default="offline")
    next_batch = Column(String(100), nullable=True)
    outcomes = Column(Text, nullable=True)

    profile = relationship("BusinessProfile", back_populates="services")


class ProfileClaim(Base):
    __tablename__ = "profile_claims"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(500), nullable=False)
    proof_link = Column(String(500), nullable=True)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    profile = relationship("BusinessProfile", back_populates="claims")


class ProfileSocialAccount(Base):
    __tablename__ = "profile_social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)
    url_or_handle = Column(String(500), nullable=False)
    verified = Column(Boolean, default=False)

    profile = relationship("BusinessProfile", back_populates="social_accounts")

