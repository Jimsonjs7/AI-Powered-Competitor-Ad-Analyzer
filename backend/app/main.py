import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import get_logger
from app.core.migrations import run_migrations
from app.jobs.scheduler import scheduler_daemon_loop

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and media directories
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)
    os.makedirs(os.path.join(settings.media_storage_dir, "creatives"), exist_ok=True)
    os.makedirs(os.path.join(settings.media_storage_dir, "posters"), exist_ok=True)
    logger.info("Database schema and media storage initialized.")

    scheduler_task = None
    if settings.auto_scrape_enabled:
        logger.info("Auto-scraping enabled. Launching background scraping daemon...")
        scheduler_task = asyncio.create_task(scheduler_daemon_loop())

    yield

    if scheduler_task:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass

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
