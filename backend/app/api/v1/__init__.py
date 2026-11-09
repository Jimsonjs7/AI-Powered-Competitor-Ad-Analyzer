from fastapi import APIRouter
from app.api.v1.ads import router as ads_router
from app.api.v1.competitors import router as competitors_router
from app.api.v1.discovery import router as discovery_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.health import router as health_router
from app.api.v1.opportunities import router as opportunities_router
from app.api.v1.posters import router as posters_router
from app.api.v1.profile import router as profile_router
from app.api.v1.weaknesses import router as weaknesses_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(profile_router)
api_router.include_router(discovery_router)
api_router.include_router(competitors_router)
api_router.include_router(weaknesses_router)
api_router.include_router(evidence_router)
api_router.include_router(opportunities_router)
api_router.include_router(ads_router)
api_router.include_router(posters_router)
api_router.include_router(health_router)
