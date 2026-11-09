import re
from urllib.parse import parse_qs, urlparse
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import get_logger
from app.models.competitor import Competitor
from app.schemas.competitor import (
    CompetitorCreate,
    CompetitorDiscoverItem,
    CompetitorDiscoverRequest,
    CompetitorResponse,
    ConfidenceLevel,
    PageResolveResponse,
)

logger = get_logger("service.competitor")


class CompetitorService:
    # Curated regional directory for zero-dependency local discovery
    DIRECTORY = {
        "Coimbatore": [
            {"name": "Nexora Academy", "course": "AI", "page_id": "page_nexora_coimbatore", "conf": ConfidenceLevel.high},
            {"name": "Growth Lab", "course": "Digital marketing", "page_id": "page_growthlab_cbe", "conf": ConfidenceLevel.high},
            {"name": "Lumen Design School", "course": "UI/UX", "page_id": "page_lumen_design", "conf": ConfidenceLevel.high},
            {"name": "CodeBridge Institute", "course": "AI", "page_id": "page_codebridge_cbe", "conf": ConfidenceLevel.high},
            {"name": "Pixel & Pen Institute", "course": "UI/UX", "page_id": "page_pixelpen_cbe", "conf": ConfidenceLevel.needs_review},
            {"name": "Skillhub Tech", "course": "Digital marketing", "page_id": "page_skillhub_tech", "conf": ConfidenceLevel.high},
            {"name": "Appin Technology Lab", "course": "AI", "page_id": "appin_coimbatore", "conf": ConfidenceLevel.medium},
            {"name": "KGISL MicroCollege", "course": "AI", "page_id": "kgisl_microcollege", "conf": ConfidenceLevel.high},
            {"name": "FITA Academy Coimbatore", "course": "Digital marketing", "page_id": "fita_coimbatore", "conf": ConfidenceLevel.medium},
        ],
        "Kochi": [
            {"name": "LCC Infotech Kochi", "course": "AI", "page_id": "lcc_kochi", "conf": ConfidenceLevel.medium},
            {"name": "Zeblearn Technologies", "course": "Digital marketing", "page_id": "zeblearn_kochi", "conf": ConfidenceLevel.medium},
            {"name": "Edoxi Training Institute", "course": "UI/UX", "page_id": "edoxi_kochi", "conf": ConfidenceLevel.high},
        ],
        "Bengaluru": [
            {"name": "ExcelR Bengaluru", "course": "AI", "page_id": "excelr_blr", "conf": ConfidenceLevel.high},
            {"name": "Digital Academy 360", "course": "Digital marketing", "page_id": "da360_blr", "conf": ConfidenceLevel.high},
            {"name": "DesignBoat UI/UX School", "course": "UI/UX", "page_id": "designboat_blr", "conf": ConfidenceLevel.high},
        ],
    }

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

    def resolve_page_id(self, input_text: str) -> PageResolveResponse:
        text = input_text.strip()

        # Check for Meta Ad Library URL format with view_all_page_id
        if "view_all_page_id=" in text:
            parsed = urlparse(text)
            params = parse_qs(parsed.query)
            page_ids = params.get("view_all_page_id")
            if page_ids:
                return PageResolveResponse(
                    resolved_name=f"Page {page_ids[0]}",
                    resolved_page_id=page_ids[0],
                    confidence=ConfidenceLevel.high,
                    source="meta_ad_library_url",
                )

        # Check for direct facebook.com or instagram.com URL
        if "facebook.com" in text or "instagram.com" in text:
            path_parts = [p for p in urlparse(text).path.split("/") if p]
            if path_parts:
                candidate = path_parts[0]
                if candidate in ("profile.php", "pages"):
                    query_id = parse_qs(urlparse(text).query).get("id")
                    candidate = query_id[0] if query_id else candidate
                return PageResolveResponse(
                    resolved_name=candidate.replace(".", " ").title(),
                    resolved_page_id=f"page_{candidate.lower()}",
                    confidence=ConfidenceLevel.high,
                    source="social_profile_url",
                )

        # Institute name search in local database
        existing = (
            self.db.query(Competitor)
            .filter(Competitor.name.ilike(f"%{text}%"))
            .first()
        )
        if existing and existing.fb_page_id:
            return PageResolveResponse(
                resolved_name=existing.name,
                resolved_page_id=existing.fb_page_id,
                confidence=ConfidenceLevel(existing.confidence),
                source="database_match",
            )

        # Search directory
        for city_list in self.DIRECTORY.values():
            for item in city_list:
                if text.lower() in item["name"].lower():
                    return PageResolveResponse(
                        resolved_name=item["name"],
                        resolved_page_id=item["page_id"],
                        confidence=item["conf"],
                        source="directory_match",
                    )

        # Fallback heuristic
        clean_slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
        return PageResolveResponse(
            resolved_name=text,
            resolved_page_id=f"page_{clean_slug}",
            confidence=ConfidenceLevel.needs_review,
            source="heuristic_fallback",
        )

    def discover_competitors(self, req: CompetitorDiscoverRequest) -> List[CompetitorDiscoverItem]:
        city_items = self.DIRECTORY.get(req.city, self.DIRECTORY["Coimbatore"])
        results = []

        for item in city_items:
            if req.query and req.query.lower() not in item["name"].lower() and req.query.lower() not in item["course"].lower():
                continue
            results.append(
                CompetitorDiscoverItem(
                    name=item["name"],
                    city=req.city,
                    course=item["course"],
                    suggested_page_id=item["page_id"],
                    confidence=item["conf"],
                )
            )
            if len(results) >= req.limit:
                break

        return results

    def create_competitor(self, data: CompetitorCreate) -> Competitor:
        existing = self.db.query(Competitor).filter(Competitor.name == data.name).first()
        if existing:
            return existing

        resolved_page_id = data.fb_page_id
        confidence = ConfidenceLevel.high.value

        # Resolve Page ID if not provided or if URL passed
        if not resolved_page_id:
            resolved = self.resolve_page_id(data.fb_page_url or data.name)
            resolved_page_id = resolved.resolved_page_id
            confidence = resolved.confidence.value

        competitor = Competitor(
            name=data.name,
            city=data.city,
            course=data.course,
            website=data.website,
            fb_page_id=resolved_page_id,
            confidence=confidence,
            is_active=True,
        )
        self.db.add(competitor)
        self.db.commit()
        self.db.refresh(competitor)
        return competitor

    def seed_initial_competitors(self):
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
