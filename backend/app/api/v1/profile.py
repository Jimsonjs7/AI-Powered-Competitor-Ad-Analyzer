from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.schemas.profile import (
    AutofillResponse,
    BusinessProfileResponse,
    BusinessProfileUpdate,
    ProfileCompletenessResponse,
)
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"], dependencies=[AuthDependency])


class AutofillRequest(BaseModel):
    website_url: str


@router.get("", response_model=BusinessProfileResponse)
def get_profile(db: Session = DbDependency):
    service = ProfileService(db)
    profile = service.get_active_profile()
    if not profile:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return BusinessProfileResponse(
            id=0,
            version=1,
            name="",
            description=None,
            tagline=None,
            business_type=["training academy"],
            domains=["AI", "Digital marketing", "UI/UX"],
            city="Coimbatore",
            area=None,
            lat=None,
            lng=None,
            radius_km=10.0,
            website=None,
            tone="Professional and outcome-focused",
            target_audience=None,
            price_positioning="mid",
            languages=["English"],
            primary_goal="enquiries",
            monthly_budget_range=None,
            preferred_cta="Book a free demo",
            thresholds={"min_ads": 3, "min_reviews": 20, "min_comments": 15},
            is_active=False,
            created_at=now,
            updated_at=now,
            services=[],
            claims=[],
            social_accounts=[],
        )
    return service.to_response(profile)


@router.put("", response_model=BusinessProfileResponse)
def update_profile(
    payload: BusinessProfileUpdate,
    db: Session = DbDependency,
):
    service = ProfileService(db)
    return service.upsert_profile(payload)


@router.get("/completeness", response_model=ProfileCompletenessResponse)
def get_completeness(db: Session = DbDependency):
    service = ProfileService(db)
    return service.get_completeness()


@router.post("/autofill", response_model=AutofillResponse)
def autofill_profile(
    payload: AutofillRequest,
    db: Session = DbDependency,
):
    service = ProfileService(db)
    return service.autofill_from_website(payload.website_url)
