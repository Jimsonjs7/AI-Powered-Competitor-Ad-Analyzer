from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.schemas.profile import (
    AutofillResponse,
    BusinessProfileCreate,
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
        # Return default initialized profile for BrandMonk
        default_create = BusinessProfileCreate(
            name="BrandMonk Academy",
            city="Coimbatore",
            domains=["AI", "Digital marketing", "UI/UX"],
        )
        return service.upsert_profile(default_create)
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
