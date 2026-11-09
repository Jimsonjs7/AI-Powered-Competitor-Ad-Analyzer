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
    def __init__(self, db: Session):
        self.db = db

    def list_competitors(self, city: Optional[str] = None) -> List[CompetitorResponse]:
        query = self.db.query(Competitor)
        if city:
            query = query.filter(Competitor.city.ilike(f"%{city}%"))
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
                    resolved_page_id=candidate.lower(),
                    confidence=ConfidenceLevel.high,
                    source="social_profile_url",
                )

        # Institute name search in local live database
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

        # Dynamic fallback: clean slug marked for user review
        clean_slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
        return PageResolveResponse(
            resolved_name=text,
            resolved_page_id=f"page_{clean_slug}",
            confidence=ConfidenceLevel.needs_review,
            source="heuristic_fallback",
        )

    def discover_competitors(self, req: CompetitorDiscoverRequest) -> List[CompetitorDiscoverItem]:
        query = self.db.query(Competitor)
        if req.city:
            query = query.filter(Competitor.city.ilike(f"%{req.city}%"))
        if req.query:
            query = query.filter(
                (Competitor.name.ilike(f"%{req.query}%")) | (Competitor.course.ilike(f"%{req.query}%"))
            )
        db_matches = query.limit(req.limit).all()

        results = [
            CompetitorDiscoverItem(
                name=c.name,
                city=c.city,
                course=c.course,
                suggested_page_id=c.fb_page_id or f"page_{c.name.lower().replace(' ', '_')}",
                confidence=ConfidenceLevel(c.confidence),
            )
            for c in db_matches
        ]

        # If database has no matches for the query, generate a discover suggestion from input
        if not results and req.query:
            clean_slug = re.sub(r"[^a-zA-Z0-9]+", "_", req.query.lower()).strip("_")
            results.append(
                CompetitorDiscoverItem(
                    name=req.query.title(),
                    city=req.city,
                    course="AI",
                    suggested_page_id=f"page_{clean_slug}",
                    confidence=ConfidenceLevel.needs_review,
                )
            )

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
