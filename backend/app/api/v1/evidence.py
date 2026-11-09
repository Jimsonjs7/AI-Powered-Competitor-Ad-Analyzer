from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.models.competitor import Competitor
from app.schemas.evidence import EvidenceImportRequest, EvidenceItemResponse, EvidenceListResponse
from app.services.evidence_service import EvidenceService

router = APIRouter(prefix="", tags=["evidence"], dependencies=[AuthDependency])


@router.post("/evidence/import", response_model=EvidenceItemResponse)
def import_evidence(
    payload: EvidenceImportRequest,
    db: Session = DbDependency,
):
    comp = db.query(Competitor).filter(Competitor.id == payload.competitor_id).first()
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found.")

    service = EvidenceService(db)
    try:
        item = service.add_evidence(
            competitor_id=payload.competitor_id,
            source=payload.source,
            text=payload.text,
            category=payload.category,
            ad_id=payload.ad_id,
        )
        return EvidenceItemResponse(
            id=item.id,
            competitor_id=item.competitor_id,
            ad_id=item.ad_id,
            source=item.source,
            text=item.text,
            language=item.language,
            sentiment=item.sentiment,
            category=item.category,
            collected_at=item.collected_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/competitors/{competitor_id}/evidence", response_model=EvidenceListResponse)
def get_competitor_evidence(
    competitor_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = DbDependency,
):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found.")

    service = EvidenceService(db)
    return service.get_evidence_for_competitor(competitor_id, page=page, page_size=page_size)

