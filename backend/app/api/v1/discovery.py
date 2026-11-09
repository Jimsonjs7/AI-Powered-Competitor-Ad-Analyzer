import asyncio
import json
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.schemas.discovery import (
    DiscoveryRunRequest,
    DiscoveryRunResponse,
    DiscoveryStatusResponse,
)
from app.services.discovery_service import DiscoveryService
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/discovery", tags=["discovery"], dependencies=[AuthDependency])


@router.post("/run", response_model=DiscoveryRunResponse)
def start_discovery_run(
    payload: DiscoveryRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = DbDependency,
):
    profile_service = ProfileService(db)
    profile = profile_service.get_active_profile()
    city = profile.city if profile else "Coimbatore"
    domains = json.loads(profile.domains_json) if profile and profile.domains_json else ["AI", "Digital marketing"]

    search_terms = payload.search_terms or [f"{d} course" for d in domains]

    discovery_service = DiscoveryService(db)
    run = discovery_service.create_run(radius_km=payload.radius_km, search_terms=search_terms)

    # Launch background task
    background_tasks.add_task(
        DiscoveryService.execute_discovery_async,
        run_id=run.id,
        city=city,
        search_terms=search_terms,
    )

    return DiscoveryRunResponse(
        run_id=run.id,
        status="running",
        message="Competitor discovery agent started.",
    )


@router.get("/{run_id}/status", response_model=DiscoveryStatusResponse)
def get_run_status(
    run_id: int,
    db: Session = DbDependency,
):
    service = DiscoveryService(db)
    run = service.get_run_status(run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discovery run not found.")

    counts = json.loads(run.counts_json) if run.counts_json else {}
    filters = json.loads(run.filters_json) if run.filters_json else {}

    return DiscoveryStatusResponse(
        run_id=run.id,
        status=run.status,
        current_step=run.current_step,
        radius_km=run.radius_km,
        filters=filters,
        counts=counts,
        cost_usd=run.cost_usd,
        started_at=run.started_at,
        finished_at=run.finished_at,
    )


@router.post("/{run_id}/cancel")
def cancel_discovery_run(
    run_id: int,
    db: Session = DbDependency,
):
    service = DiscoveryService(db)
    cancelled = service.cancel_run(run_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not cancel run (either not found or not currently running).",
        )
    return {"status": "cancelled", "run_id": run_id}
