from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.logging import get_logger
from app.services.ad_service import AdService
from app.services.competitor_service import CompetitorService

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified and initialized.")

    # Seed initial competitors and ads if empty (instant local seed)
    db = SessionLocal()
    try:
        comp_service = CompetitorService(db)
        comp_service.seed_initial_competitors()

        from app.models.ad import Ad
        from app.models.competitor import Competitor
        if db.query(Ad).count() == 0:
            first_comp = db.query(Competitor).first()
            if first_comp:
                ad_service = AdService(db)
                ad_service.collect_ads_for_competitor(first_comp.id)
                logger.info("Initial seed ads verified.")
    finally:
        db.close()

    yield
    logger.info("Application shutdown completed.")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url=None,
)

# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["health"])
def root_health():
    return {"status": "ok", "app": settings.app_name}

