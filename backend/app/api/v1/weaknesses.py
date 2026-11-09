from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.models.competitor import Competitor
from app.schemas.weakness import DataSufficiencyResponse, WeaknessListResponse, WeaknessResponse
from app.services.weakness_service import WeaknessService

router = APIRouter(prefix="/competitors", tags=["weaknesses"], dependencies=[AuthDependency])


@router.get("/{competitor_id}/sufficiency", response_model=DataSufficiencyResponse)
def get_data_sufficiency(
    competitor_id: int,
    db: Session = DbDependency,
):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found.")

    service = WeaknessService(db)
    return service.check_data_sufficiency(competitor_id)


@router.post("/{competitor_id}/analyze", response_model=List[WeaknessResponse])
def analyze_competitor_weaknesses(
    competitor_id: int,
    db: Session = DbDependency,
):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found.")

    service = WeaknessService(db)
    sufficiency = service.check_data_sufficiency(competitor_id)
    if not sufficiency.is_sufficient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Data insufficient for reliable weakness analysis.",
                "missing": sufficiency.missing,
            },
        )

    return service.analyze_competitor(competitor_id)


@router.get("/{competitor_id}/weaknesses", response_model=WeaknessListResponse)
def get_competitor_weaknesses(
    competitor_id: int,
    db: Session = DbDependency,
):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found.")

    service = WeaknessService(db)
    return service.list_weaknesses_for_competitor(competitor_id)
