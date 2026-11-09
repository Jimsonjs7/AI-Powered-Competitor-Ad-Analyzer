from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.schemas.competitor import CompetitorCreate, CompetitorResponse
from app.services.competitor_service import CompetitorService

router = APIRouter(prefix="/competitors", tags=["competitors"], dependencies=[AuthDependency])


@router.get("", response_model=List[CompetitorResponse])
def get_competitors(
    city: Optional[str] = Query(None, description="Filter competitors by city"),
    db: Session = DbDependency,
):
    service = CompetitorService(db)
    return service.list_competitors(city=city)


@router.post("", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
def add_competitor(
    payload: CompetitorCreate,
    db: Session = DbDependency,
):
    service = CompetitorService(db)
    comp = service.create_competitor(payload)
    return CompetitorResponse(
        id=comp.id,
        name=comp.name,
        city=comp.city,
        course=comp.course,
        website=comp.website,
        fb_page_id=comp.fb_page_id,
        confidence=comp.confidence,
        active_ads_count=0,
        is_active=comp.is_active,
        created_at=comp.created_at,
    )
