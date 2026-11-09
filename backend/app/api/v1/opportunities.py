from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.schemas.opportunity import (
    OpportunityDraftRequest,
    OpportunityDraftResponse,
    OpportunityResponse,
)
from app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/opportunities", tags=["opportunities"], dependencies=[AuthDependency])


@router.get("", response_model=List[OpportunityResponse])
def get_opportunities(db: Session = DbDependency):
    service = OpportunityService(db)
    return service.score_opportunities()


@router.post("/draft", response_model=OpportunityDraftResponse)
def draft_opportunity_counter_ad(
    payload: OpportunityDraftRequest,
    db: Session = DbDependency,
):
    service = OpportunityService(db)
    try:
        return service.generate_draft(payload.opportunity_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
