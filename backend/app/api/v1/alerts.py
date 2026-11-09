from typing import List
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.schemas.alert import AlertResponse, WeeklyDigestResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="", tags=["alerts"], dependencies=[AuthDependency])


@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    unread_only: bool = Query(False, description="Filter for unread alerts only"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = DbDependency,
):
    service = AlertService(db)
    return service.list_alerts(unread_only=unread_only, limit=limit)


@router.post("/alerts/{alert_id}/read")
def mark_alert_read(
    alert_id: int,
    db: Session = DbDependency,
):
    service = AlertService(db)
    success = service.mark_read(alert_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return {"status": "ok", "alert_id": alert_id}


@router.post("/alerts/read-all")
def mark_all_alerts_read(
    db: Session = DbDependency,
):
    service = AlertService(db)
    count = service.mark_all_read()
    return {"status": "ok", "marked_read": count}


@router.get("/digest", response_model=WeeklyDigestResponse)
def get_weekly_digest(
    db: Session = DbDependency,
):
    service = AlertService(db)
    return service.get_weekly_digest()

