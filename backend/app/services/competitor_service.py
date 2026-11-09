import re
from urllib.parse import parse_qs, urlparse
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import get_logger
from app.models.competitor import Competitor
from app.models.competitor_metrics import CompetitorMetrics
from app.schemas.competitor import (
    CompetitorCreate,
    CompetitorDiscoverItem,
    CompetitorDiscoverRequest,
    CompetitorMetricsResponse,
    CompetitorResponse,
    ConfidenceLevel,
    PageResolveResponse,
)

logger = get_logger("service.competitor")


class CompetitorService:
    def __init__(self, db: Session):
        self.db = db

    def _to_response(self, c: Competitor) -> CompetitorResponse:
        metrics_res = None
        if c.metrics:
            metrics_res = CompetitorMetricsResponse(
                active_ads=c.metrics.active_ads,
                new_this_week=c.metrics.new_this_week,
                longest_run_days=c.metrics.longest_run_days,
                rating=c.metrics.rating,
                review_count=c.metrics.review_count,
                negative_share=c.metrics.negative_share,
                comment_count=c.metrics.comment_count,
                weakness_score=c.metrics.weakness_score,
                threat_score=c.metrics.threat_score,
                computed_at=c.metrics.computed_at,
            )

        active_count = len([a for a in c.ads if a.is_active])
        return CompetitorResponse(
            id=c.id,
            name=c.name,
            city=c.city,
            course=c.course,
            website=c.website,
            fb_page_id=c.fb_page_id,
            confidence=ConfidenceLevel(c.confidence),
            active_ads_count=active_count,
            is_active=c.is_active,
            lat=c.lat,
            lng=c.lng,
            distance_km=c.distance_km,
            area=c.area,
            ig_handle=c.ig_handle,
            data_status=c.data_status or "pending",
            metrics=metrics_res,
            created_at=c.created_at,
        )

    def list_competitors(
        self,
        city: Optional[str] = None,
        sort_by: Optional[str] = None,
        has_ads: Optional[bool] = None,
        data_status: Optional[str] = None,
        max_distance_km: Optional[float] = None,
    ) -> List[CompetitorResponse]:
        query = self.db.query(Competitor)
        if city:
            query = query.filter(Competitor.city.ilike(f"%{city}%"))
        if data_status:
            query = query.filter(Competitor.data_status == data_status)
        if max_distance_km is not None:
            query = query.filter(Competitor.distance_km <= max_distance_km)

        competitors = query.all()

        if has_ads is not None:
            if has_ads:
                competitors = [c for c in competitors if any(a.is_active for a in c.ads)]
            else:
                competitors = [c for c in competitors if not any(a.is_active for a in c.ads)]

        responses = [self._to_response(c) for c in competitors]

        # Sorting logic
        if sort_by == "active_ads":
            responses.sort(key=lambda x: x.active_ads_count, reverse=True)
        elif sort_by == "distance":
            responses.sort(key=lambda x: (x.distance_km if x.distance_km is not None else 999.0))
        elif sort_by == "weakness":
            responses.sort(key=lambda x: (x.metrics.weakness_score if x.metrics else 0.0), reverse=True)
        elif sort_by == "name":
            responses.sort(key=lambda x: x.name.lower())

        return responses

    def get_competitor(self, competitor_id: int) -> Optional[CompetitorResponse]:
        c = self.db.query(Competitor).filter(Competitor.id == competitor_id).first()
        return self._to_response(c) if c else None

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
                website=c.website,
                suggested_page_id=c.fb_page_id or f"page_{c.name.lower().replace(' ', '_')}",
                confidence=ConfidenceLevel(c.confidence),
            )
            for c in db_matches
        ]

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
            lat=data.lat,
            lng=data.lng,
            distance_km=data.distance_km,
            area=data.area,
            ig_handle=data.ig_handle,
            data_status="pending",
            is_active=True,
        )
        self.db.add(competitor)
        self.db.commit()
        self.db.refresh(competitor)

        # Initialize metrics record
        metrics = CompetitorMetrics(competitor_id=competitor.id)
        self.db.add(metrics)
        self.db.commit()

        return competitor
