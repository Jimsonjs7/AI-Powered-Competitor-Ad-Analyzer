import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.core.config import settings
from app.core.security import validate_target_url
from app.jobs.scheduler import run_scrape_and_analysis_cycle
from app.models.media import AdMedia
from app.schemas.ad import AdFilterParams, AdResponse, MarketInsightResponse
from app.schemas.analysis import AdAnalysisSchema
from app.schemas.creative_recommender import CreativeCounterAdResponse
from app.services.ad_service import AdService
from app.services.analysis_service import AnalysisService
from app.services.creative_recommender_service import CreativeRecommenderService

router = APIRouter(prefix="", tags=["ads"], dependencies=[AuthDependency])


class RefreshAdsResponse(BaseModel):
    message: str
    total_ads_collected: int


class ManualImportRequest(BaseModel):
    ad_url: str
    competitor_name: str = "Manual Competitor"
    course: str = "AI"
    copy_text: str = ""
    headline: Optional[str] = None


@router.get("/ads", response_model=List[AdResponse])
def get_ads(
    competitor_ids: Optional[str] = Query(None, description="Comma-separated competitor IDs"),
    course: Optional[str] = Query("All", description="Course filter: All, AI, Digital marketing, UI/UX"),
    city: Optional[str] = Query("Coimbatore", description="City location"),
    sort_by: str = Query("days", description="Sorting field: days, score, new"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = DbDependency,
):
    service = AdService(db)
    parsed_ids = [int(x.strip()) for x in competitor_ids.split(",") if x.strip().isdigit()] if competitor_ids else None

    filters = AdFilterParams(
        competitor_ids=parsed_ids,
        course=course,
        city=city,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )
    return service.list_ads(filters)


@router.get("/ads/insights/market", response_model=MarketInsightResponse)
def get_market_insights(
    city: str = Query("Coimbatore", description="City region for market analysis"),
    db: Session = DbDependency,
):
    service = AdService(db)
    return service.get_market_insights(city=city)


@router.post("/ads/refresh", response_model=RefreshAdsResponse)
def refresh_ads(
    db: Session = DbDependency,
):
    result = run_scrape_and_analysis_cycle(db)
    return RefreshAdsResponse(
        message=f"Refreshed {result['ads_collected']} ads across {result['competitors_count']} competitors; {result['ads_analyzed']} analyzed.",
        total_ads_collected=result["ads_collected"],
    )


@router.post("/ads/{ad_id}/analyze", response_model=AdAnalysisSchema)
def analyze_ad(
    ad_id: int,
    db: Session = DbDependency,
):
    service = AnalysisService(db)
    try:
        return service.analyze_ad(ad_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ad analysis failed")


@router.post("/ads/import", response_model=RefreshAdsResponse)
def manual_import_ad(
    payload: ManualImportRequest,
    db: Session = DbDependency,
):
    validate_target_url(payload.ad_url)

    from app.providers.ads.manual_import import ManualImportProvider
    from app.services.competitor_service import CompetitorService
    from app.schemas.competitor import CompetitorCreate

    comp_service = CompetitorService(db)
    comp = comp_service.create_competitor(
        CompetitorCreate(
            name=payload.competitor_name,
            course=payload.course,
            fb_page_url=payload.ad_url,
        )
    )

    importer = ManualImportProvider()
    importer.import_from_url(
        ad_url=payload.ad_url,
        page_name=comp.name,
        copy_text=payload.copy_text,
        headline=payload.headline,
    )

    ad_service = AdService(db)
    ad_service.collect_ads_for_competitor(comp.id)

    return RefreshAdsResponse(
        message="Manual ad imported successfully.",
        total_ads_collected=1,
    )


@router.get("/media/{content_hash}")
def get_cached_media(
    content_hash: str,
    db: Session = DbDependency,
):
    media = db.query(AdMedia).filter(AdMedia.content_hash == content_hash).first()
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    file_path = os.path.join(settings.media_storage_dir, "creatives", f"{content_hash}.jpg")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/jpeg")

    return {"original_url": media.original_url}


@router.get("/ads/{ad_id}/counter-recommendations", response_model=CreativeCounterAdResponse)
@router.post("/ads/{ad_id}/counter-recommendations", response_model=CreativeCounterAdResponse)
def get_creative_counter_recommendations(
    ad_id: int,
    db: Session = DbDependency,
):
    service = CreativeRecommenderService(db)
    try:
        return service.generate_recommendations(ad_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

