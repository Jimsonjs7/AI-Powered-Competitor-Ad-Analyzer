from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate, CompetitorResponse, ConfidenceLevel


class CompetitorService:
    def __init__(self, db: Session):
        self.db = db

    def list_competitors(self, city: Optional[str] = None) -> List[CompetitorResponse]:
        query = self.db.query(Competitor)
        if city:
            query = query.filter(Competitor.city == city)
        competitors = query.all()

        return [
            CompetitorResponse(
                id=c.id,
                name=c.name,
                city=c.city,
                course=c.course,
                website=c.website,
                fb_page_id=c.fb_page_id,
                confidence=ConfidenceLevel(c.confidence),
                active_ads_count=len([a for a in c.ads if a.is_active]),
                is_active=c.is_active,
                created_at=c.created_at,
            )
            for c in competitors
        ]

    def create_competitor(self, data: CompetitorCreate) -> Competitor:
        existing = self.db.query(Competitor).filter(Competitor.name == data.name).first()
        if existing:
            return existing

        confidence = ConfidenceLevel.high.value
        # If Page ID is missing or unresolved, flag as needs review
        if not data.fb_page_id:
            confidence = ConfidenceLevel.needs_review.value

        competitor = Competitor(
            name=data.name,
            city=data.city,
            course=data.course,
            website=data.website,
            fb_page_id=data.fb_page_id,
            confidence=confidence,
            is_active=True,
        )
        self.db.add(competitor)
        self.db.commit()
        self.db.refresh(competitor)
        return competitor

    def seed_initial_competitors(self):
        # Initial verified competitors in Coimbatore matching reference design
        defaults = [
            ("Nexora Academy", "AI", "page_nexora_coimbatore", "high"),
            ("Growth Lab", "Digital marketing", "page_growthlab_cbe", "high"),
            ("Lumen Design School", "UI/UX", "page_lumen_design", "high"),
            ("CodeBridge Institute", "AI", "page_codebridge_cbe", "high"),
            ("Pixel & Pen Institute", "UI/UX", "page_pixelpen_cbe", "needs_review"),
            ("Skillhub Tech", "Digital marketing", "page_skillhub_tech", "high"),
        ]
        for name, course, page_id, conf in defaults:
            existing = self.db.query(Competitor).filter(Competitor.name == name).first()
            if not existing:
                c = Competitor(
                    name=name,
                    city="Coimbatore",
                    course=course,
                    fb_page_id=page_id,
                    confidence=conf,
                    is_active=True,
                )
                self.db.add(c)
        self.db.commit()
