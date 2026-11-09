from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ProfileServiceCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    fee_min: Optional[float] = None
    fee_max: Optional[float] = None
    duration: Optional[str] = None
    mode: str = "offline"
    next_batch: Optional[str] = None
    outcomes: Optional[str] = None


class ProfileServiceResponse(ProfileServiceCreate):
    id: int
    profile_id: int


class ProfileClaimCreate(BaseModel):
    text: str = Field(..., max_length=500)
    proof_link: Optional[str] = None
    approved: bool = False


class ProfileClaimResponse(ProfileClaimCreate):
    id: int
    profile_id: int
    created_at: datetime


class ProfileSocialAccountCreate(BaseModel):
    platform: str = Field(..., max_length=50)
    url_or_handle: str = Field(..., max_length=500)
    verified: bool = False


class ProfileSocialAccountResponse(ProfileSocialAccountCreate):
    id: int
    profile_id: int


class BusinessProfileCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    tagline: Optional[str] = None
    business_type: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    city: str = Field(default="Coimbatore")
    area: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: float = 10.0
    website: Optional[str] = None
    tone: str = "Professional and outcome-focused"
    target_audience: Optional[str] = None
    price_positioning: str = "mid"
    languages: List[str] = Field(default_factory=lambda: ["English"])
    primary_goal: str = "enquiries"
    monthly_budget_range: Optional[str] = None
    preferred_cta: str = "Book a free demo"
    thresholds: Dict[str, int] = Field(
        default_factory=lambda: {"min_ads": 3, "min_reviews": 20, "min_comments": 15}
    )
    services: List[ProfileServiceCreate] = Field(default_factory=list)
    claims: List[ProfileClaimCreate] = Field(default_factory=list)
    social_accounts: List[ProfileSocialAccountCreate] = Field(default_factory=list)


class BusinessProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tagline: Optional[str] = None
    business_type: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    city: Optional[str] = None
    area: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: Optional[float] = None
    website: Optional[str] = None
    tone: Optional[str] = None
    target_audience: Optional[str] = None
    price_positioning: Optional[str] = None
    languages: Optional[List[str]] = None
    primary_goal: Optional[str] = None
    monthly_budget_range: Optional[str] = None
    preferred_cta: Optional[str] = None
    thresholds: Optional[Dict[str, int]] = None
    services: Optional[List[ProfileServiceCreate]] = None
    claims: Optional[List[ProfileClaimCreate]] = None
    social_accounts: Optional[List[ProfileSocialAccountCreate]] = None


class BusinessProfileResponse(BaseModel):
    id: int
    version: int
    name: str
    description: Optional[str]
    tagline: Optional[str]
    business_type: List[str]
    domains: List[str]
    city: str
    area: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    radius_km: float
    website: Optional[str]
    tone: str
    target_audience: Optional[str]
    price_positioning: str
    languages: List[str]
    primary_goal: str
    monthly_budget_range: Optional[str]
    preferred_cta: str
    thresholds: Dict[str, int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    services: List[ProfileServiceResponse] = Field(default_factory=list)
    claims: List[ProfileClaimResponse] = Field(default_factory=list)
    social_accounts: List[ProfileSocialAccountResponse] = Field(default_factory=list)


class CompletenessHint(BaseModel):
    field: str
    hint: str
    impact: str


class ProfileCompletenessResponse(BaseModel):
    score: int
    missing_fields: List[CompletenessHint]
    is_ready_for_discovery: bool


class AutofillSuggestion(BaseModel):
    field: str
    suggested_value: str
    source_url: str
    requires_confirmation: bool = True


class AutofillResponse(BaseModel):
    website_title: Optional[str] = None
    website_description: Optional[str] = None
    suggestions: List[AutofillSuggestion] = Field(default_factory=list)
