from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.api.deps import DbDependency
from app.schemas.scrape_run import HealthStatusResponse
from app.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthStatusResponse)
def get_health_status(db: Session = DbDependency):
    service = HealthService(db)
    return service.check_providers()

