import os
from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import AuthDependency, DbDependency
from app.models.poster import Poster
from app.schemas.poster import (
    PosterPromptRequest,
    PosterPromptResponse,
    PosterRenderRequest,
    PosterRenderResponse,
)
from app.services.poster_service import PosterService

router = APIRouter(prefix="/posters", tags=["posters"], dependencies=[AuthDependency])


@router.post("/prompt", response_model=PosterPromptResponse)
def generate_prompt(
    payload: PosterPromptRequest,
    db: Session = DbDependency,
):
    service = PosterService(db)
    return service.generate_prompt(payload)


@router.post("/render", response_model=PosterRenderResponse)
def render_poster(
    payload: PosterRenderRequest,
    db: Session = DbDependency,
):
    service = PosterService(db)
    return service.render_poster(payload)


@router.get("/{poster_id}/image")
def get_poster_image(
    poster_id: int,
    db: Session = DbDependency,
):
    poster = db.query(Poster).filter(Poster.id == poster_id).first()
    if not poster or not poster.image_path or not os.path.exists(poster.image_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poster image not found")

    return FileResponse(poster.image_path, media_type="image/png")

