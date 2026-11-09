from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.schemas.competitor import (
    CompetitorCrawlRequest,
    CompetitorCrawlResponse,
    CompetitorCreate,
    CompetitorDiscoverItem,
    CompetitorDiscoverRequest,
    CompetitorResponse,
    PageResolveRequest,
    PageResolveResponse,
)
from app.services.competitor_service import CompetitorService

router = APIRouter(prefix="/competitors", tags=["competitors"], dependencies=[AuthDependency])


@router.get("", response_model=List[CompetitorResponse])
def get_competitors(
    city: Optional[str] = Query(None, description="Filter competitors by city"),
    sort_by: Optional[str] = Query(None, description="Sort: active_ads, distance, weakness, name"),
    has_ads: Optional[bool] = Query(None, description="Filter competitors with/without active ads"),
    data_status: Optional[str] = Query(None, description="Filter by data sufficiency status"),
    max_distance_km: Optional[float] = Query(None, description="Max distance in km from profile location"),
    db: Session = DbDependency,
):
    service = CompetitorService(db)
    return service.list_competitors(
        city=city,
        sort_by=sort_by,
        has_ads=has_ads,
        data_status=data_status,
        max_distance_km=max_distance_km,
    )


@router.get("/{competitor_id}", response_model=CompetitorResponse)
def get_competitor(
    competitor_id: int,
    db: Session = DbDependency,
):
    service = CompetitorService(db)
    comp = service.get_competitor(competitor_id)
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found.")
    return comp


@router.post("", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
def add_competitor(
    payload: CompetitorCreate,
    db: Session = DbDependency,
):
    service = CompetitorService(db)
    comp = service.create_competitor(payload)
    return service.get_competitor(comp.id)


@router.post("/discover", response_model=List[CompetitorDiscoverItem])
def discover_competitors(
    payload: CompetitorDiscoverRequest,
    db: Session = DbDependency,
):
    service = CompetitorService(db)
    return service.discover_competitors(payload)


@router.post("/resolve", response_model=PageResolveResponse)
def resolve_page_id(
    payload: PageResolveRequest,
    db: Session = DbDependency,
):
    service = CompetitorService(db)
    return service.resolve_page_id(payload.input_text)


@router.post("/crawl-website", response_model=CompetitorCrawlResponse)
def crawl_competitor_website(
    payload: CompetitorCrawlRequest,
    db: Session = DbDependency,
):
    service = CompetitorService(db)
    return service.crawl_competitor_website(payload.website_url)
