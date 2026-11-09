from fastapi import APIRouter
from app.api.v1.ads import router as ads_router
from app.api.v1.competitors import router as competitors_router
from app.api.v1.health import router as health_router
from app.api.v1.posters import router as posters_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(competitors_router)
api_router.include_router(ads_router)
api_router.include_router(posters_router)
api_router.include_router(health_router)

