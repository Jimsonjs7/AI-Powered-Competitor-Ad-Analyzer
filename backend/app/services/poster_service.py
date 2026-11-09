from typing import Optional
from sqlalchemy.orm import Session
from app.models.ad import Ad
from app.models.poster import Poster
from app.providers.images.pillow_overlay import PillowPosterRenderer
from app.schemas.poster import (
    PosterPromptRequest,
    PosterPromptResponse,
    PosterRenderRequest,
    PosterRenderResponse,
)


class PosterService:
    ANGLES = [
        {
            "name": "Outcome",
            "strategy": "a clear result promised in a fixed time",
            "composition": "bold headline top-left, one calm illustration of a learner at a laptop, empty band at the bottom for a button",
            "headlines": {
                "AI": "Build real AI projects in 12 weeks",
                "Digital marketing": "Launch your first paid campaign by week 3",
                "UI/UX": "Go from Figma basics to a hiring-ready portfolio",
            },
            "subline": "Small batches, live mentors, weekly reviews",
        },
        {
            "name": "Proof",
            "strategy": "trust built through mentors and reviewed work",
            "composition": "split composition with a mentor portrait area on the right and a clean text zone on the left",
            "headlines": {
                "AI": "Learn AI from engineers who ship it",
                "Digital marketing": "Learn marketing from people who run ad budgets",
                "UI/UX": "Every design project reviewed by a working designer",
            },
            "subline": "Industry mentors on every batch",
        },
        {
            "name": "Urgency",
            "strategy": "a real start date and a limited seat count",
            "composition": "strong colour block with a large date badge in the corner and minimal imagery",
            "headlines": {
                "AI": "AI batch starts soon. Seats are limited",
                "Digital marketing": "Digital marketing batch is filling fast",
                "UI/UX": "New UI/UX batch. Few seats left",
            },
            "subline": "Next batch starts in 2 weeks",
        },
    ]

    def __init__(self, db: Session):
        self.db = db
        self.renderer = PillowPosterRenderer()

    def generate_prompt(self, req: PosterPromptRequest) -> PosterPromptResponse:
        angle = self.ANGLES[min(req.angle_index, len(self.ANGLES) - 1)]
        course_key = req.course if req.course in angle["headlines"] else "AI"
        headline = angle["headlines"][course_key]
        subline = angle["subline"]
        cta = "Book a free demo"

        ad = self.db.query(Ad).filter(Ad.id == req.ad_id).first()
        hook_name = ad.analysis.hook.lower() if ad and ad.analysis else "competitor result promise"

        size_label = "square 1:1" if req.size_format == "square" else "story 9:16" if req.size_format == "story" else "feed 4:5"

        prompt = (
            f"Social media poster, {size_label} format, for BrandMonk Academy's {course_key} course. "
            f"Strategy: {angle['strategy']}, inspired by a competitor ad built on \"{hook_name}\". "
            f"Composition: {angle['composition']}. "
            f"Palette: navy #16202E, blue #1F4FD8 and sun #F2B84B on white. "
            f"Mood: confident and professional, for students and young professionals in South India. "
            f"Leave clean space for text and logo. Draw no lettering in the image."
        )

        return PosterPromptResponse(
            ad_id=req.ad_id,
            course=course_key,
            angle_name=angle["name"],
            headline=headline,
            subline=subline,
            cta_text=cta,
            prompt=prompt,
            size_format=req.size_format,
        )

    def render_poster(self, req: PosterRenderRequest) -> PosterRenderResponse:
        prompt_data = self.generate_prompt(
            PosterPromptRequest(
                ad_id=req.ad_id,
                course=req.course,
                angle_index=req.angle_index,
                size_format=req.size_format,
            )
        )

        final_head = req.custom_headline or prompt_data.headline
        final_sub = req.custom_subline or prompt_data.subline
        final_cta = req.custom_cta or prompt_data.cta_text

        poster_obj = Poster(
            source_ad_id=req.ad_id,
            course=req.course,
            angle_name=prompt_data.angle_name,
            size_format=req.size_format,
            headline=final_head,
            subline=final_sub,
            cta_text=final_cta,
            prompt=prompt_data.prompt,
        )
        self.db.add(poster_obj)
        self.db.commit()
        self.db.refresh(poster_obj)

        filepath = self.renderer.render(
            poster_id=poster_obj.id,
            headline=final_head,
            subline=final_sub,
            cta_text=final_cta,
            size_format=req.size_format,
        )

        poster_obj.image_path = filepath
        self.db.commit()

        return PosterRenderResponse(
            poster_id=poster_obj.id,
            headline=final_head,
            subline=final_sub,
            cta_text=final_cta,
            image_url=f"/api/v1/posters/{poster_obj.id}/image",
            size_format=req.size_format,
            status="rendered",
        )

