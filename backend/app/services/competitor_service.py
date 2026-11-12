import re
from urllib.parse import parse_qs, urlparse
from typing import List, Optional
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import validate_target_url
from app.models.competitor import Competitor
from app.models.competitor_metrics import CompetitorMetrics
from app.schemas.competitor import (
    CompetitorCrawlResponse,
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
        comp_name = data.name.strip()
        comp_city = data.city.strip() if data.city else "Coimbatore"
        comp_course = data.course or "Digital marketing"
        comp_website = data.website
        comp_area = data.area
        comp_fb_page_id = data.fb_page_id
        comp_ig_handle = data.ig_handle
        confidence = ConfidenceLevel.high.value

        # Auto-detect if name or website is a website URL
        input_is_url = comp_name.startswith("http://") or comp_name.startswith("https://")
        if input_is_url and not any(d in comp_name.lower() for d in ["facebook.com", "instagram.com"]):
            comp_website = comp_name
            try:
                crawl_res = self.crawl_competitor_website(comp_website)
                comp_name = crawl_res.name
                comp_course = crawl_res.course or comp_course
                comp_city = crawl_res.city or comp_city
                comp_area = crawl_res.area or comp_area
                comp_fb_page_id = crawl_res.fb_page_id or comp_fb_page_id
                comp_ig_handle = crawl_res.ig_handle or comp_ig_handle
            except Exception as e:
                logger.warning(f"Auto-crawl for competitor URL {comp_website} failed: {e}")

        # Check for existing competitor by name or website
        existing = self.db.query(Competitor).filter(
            (Competitor.name == comp_name) | 
            (Competitor.website == comp_website if comp_website else False)
        ).first()
        if existing:
            # Refresh/collect ads if empty
            try:
                from app.services.ad_service import AdService
                AdService(self.db).collect_ads_for_competitor(existing.id)
            except Exception as e:
                logger.warning(f"Ad collection for existing competitor {existing.name} failed: {e}")
            return existing

        if not comp_fb_page_id:
            resolved = self.resolve_page_id(data.fb_page_url or comp_name)
            comp_fb_page_id = resolved.resolved_page_id
            confidence = resolved.confidence.value

        competitor = Competitor(
            name=comp_name,
            city=comp_city,
            course=comp_course,
            website=comp_website,
            fb_page_id=comp_fb_page_id,
            confidence=confidence,
            lat=data.lat,
            lng=data.lng,
            distance_km=data.distance_km,
            area=comp_area,
            ig_handle=comp_ig_handle,
            data_status="ready",
            is_active=True,
        )
        self.db.add(competitor)
        self.db.commit()
        self.db.refresh(competitor)

        # Initialize metrics record
        metrics = CompetitorMetrics(competitor_id=competitor.id)
        self.db.add(metrics)
        self.db.commit()

        # Immediately collect ads for newly created competitor
        try:
            from app.services.ad_service import AdService
            ad_service = AdService(self.db)
            ad_service.collect_ads_for_competitor(competitor.id)
            self.db.refresh(competitor)
        except Exception as e:
            logger.warning(f"Immediate ad collection for new competitor {competitor.name} failed: {e}")

        return competitor

    def crawl_competitor_website(self, website_url: str) -> CompetitorCrawlResponse:
        safe_url = validate_target_url(website_url, check_whitelist=False)
        name = "Competitor"
        course = "Digital marketing"
        city = "Coimbatore"
        area = None
        fb_page_id = None
        fb_url = None
        ig_handle = None
        description = None
        social_links = []

        def check_redirect_url(response: httpx.Response):
            redirect_loc = response.headers.get("Location")
            if redirect_loc:
                from urllib.parse import urljoin
                resolved_redirect = urljoin(str(response.url), redirect_loc)
                validate_target_url(resolved_redirect, check_whitelist=False)

        try:
            with httpx.Client(
                timeout=10.0,
                follow_redirects=True,
                event_hooks={"response": [check_redirect_url]},
            ) as client:
                res = client.get(safe_url, headers={"User-Agent": "BrandMonk-CompetitorDiscovery/2.0"})
                if res.status_code == 200:
                    html = res.text

                    # Extract title / name
                    title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
                    if title_match:
                        raw_title = title_match.group(1).strip()
                        parts = [p.strip() for p in re.split(r"[-|–—:]", raw_title) if p.strip()]
                        seo_indicators = ["best ", "top ", " agency in", " company in", " services in", " institute in", " training in", "academy in"]
                        if len(parts) > 1 and any(ind in parts[0].lower() for ind in seo_indicators) and not any(ind in parts[-1].lower() for ind in seo_indicators):
                            name = parts[-1]
                        else:
                            name = parts[0] if parts else raw_title

                    # Extract description
                    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE | re.DOTALL)
                    if desc_match:
                        description = desc_match.group(1).strip()

                    # If extracted name contains generic SEO phrases, derive true brand name
                    seo_indicator_words = ["best ", "top ", "leading ", "company in", "agency in", "services in", "institute in", "training in", "academy in"]
                    if any(ind in name.lower() for ind in seo_indicator_words) or name == "Competitor":
                        desc_match_brand = re.search(r'([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+){0,2})\s+(?:is|provides|offers|leads|delivers)', description or "")
                        if desc_match_brand and not any(w in desc_match_brand.group(1).lower() for w in ["best", "top", "leading"]):
                            name = desc_match_brand.group(1).strip()
                        else:
                            netloc = urlparse(safe_url).netloc.lower().replace("www.", "")
                            domain_base = netloc.split(".")[0]
                            clean_domain = re.sub(r'([a-z])([A-Z])', r'\1 \2', domain_base).title()
                            if len(clean_domain) > 2:
                                name = clean_domain

                    combined = f"{raw_title if 'raw_title' in locals() else ''} {description or ''} {html[:5000]}"

                    # Detect course / primary offer
                    if re.search(r"\b(ai|artificial intelligence|machine learning|data science)\b", combined, re.IGNORECASE):
                        course = "AI"
                    elif re.search(r"\b(ui|ux|user interface|product design)\b", combined, re.IGNORECASE):
                        course = "UI/UX"
                    elif re.search(r"\b(full stack|web development|software)\b", combined, re.IGNORECASE):
                        course = "Full Stack"
                    else:
                        course = "Digital marketing"

                    # Detect city
                    for city_cand in ["Coimbatore", "Chennai", "Bangalore", "Bengaluru", "Hyderabad", "Mumbai", "Delhi", "Kochi", "Madurai", "Trichy"]:
                        if re.search(r"\b" + re.escape(city_cand) + r"\b", combined, re.IGNORECASE):
                            city = city_cand
                            break

                    # Detect Coimbatore area / neighbourhood
                    coimbatore_areas = ["Gandhipuram", "RS Puram", "Peelamedu", "Saravanampatti", "Hopes College", "Saibaba Colony", "Singanallur", "Ramanathapuram", "Vadavalli", "Ukkadam", "Kuniyamuthur", "Thudiyalur", "Ganapathy"]
                    for a_cand in coimbatore_areas:
                        if re.search(r"\b" + re.escape(a_cand) + r"\b", combined, re.IGNORECASE):
                            area = a_cand
                            break

                    # Extract Facebook link & Page ID
                    fb_match = re.search(r'href=["\'](https?://(?:www\.)?facebook\.com/[^"\']+)["\']', html, re.IGNORECASE)
                    if fb_match:
                        fb_url = fb_match.group(1)
                        social_links.append(fb_url)
                        resolved = self.resolve_page_id(fb_url)
                        fb_page_id = resolved.resolved_page_id

                    # Extract Instagram link
                    ig_match = re.search(r'href=["\'](https?://(?:www\.)?instagram\.com/([^"\'/?]+)[^"\']*)["\']', html, re.IGNORECASE)
                    if ig_match:
                        social_links.append(ig_match.group(1))
                        ig_handle = ig_match.group(2)

                    # Extract other social links
                    all_socials = re.findall(r'href=["\'](https?://(?:www\.)?(?:linkedin|youtube|twitter|x)\.com/[^"\']+)["\']', html, re.IGNORECASE)
                    social_links.extend(all_socials)
        except Exception as e:
            logger.warning(f"Competitor crawl failed for {safe_url}: {e}")

        return CompetitorCrawlResponse(
            name=name,
            course=course,
            city=city,
            area=area,
            website=safe_url,
            fb_page_id=fb_page_id,
            fb_url=fb_url,
            ig_handle=ig_handle,
            description=description,
            detected_social_links=list(set(social_links)),
        )
