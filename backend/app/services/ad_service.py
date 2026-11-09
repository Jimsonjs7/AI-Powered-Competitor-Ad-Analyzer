import hashlib
import os
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import get_logger
from app.models.ad import Ad
from app.models.competitor import Competitor
from app.models.media import AdMedia
from app.models.scrape_run import ScrapeRun
from app.providers.ads.apify_meta import ApifyMetaProvider
from app.providers.ads.base import AdSource
from app.providers.ads.mock_provider import MockAdProvider
from app.providers.ads.playwright_adlibrary import PlaywrightAdLibraryProvider
from app.providers.ads.scrapecreators import ScrapeCreatorsProvider
from app.schemas.ad import AdFilterParams, AdRecord, AdResponse

logger = get_logger("service.ad")


class AdService:
    def __init__(self, db: Session):
        self.db = db
        # Configured provider chain fallback order
        self.chain: List[AdSource] = [
            ApifyMetaProvider(),
            ScrapeCreatorsProvider(),
            PlaywrightAdLibraryProvider(),
            MockAdProvider(),  # Verified local offline seed provider
        ]

    def list_ads(self, filters: AdFilterParams) -> List[AdResponse]:
        query = self.db.query(Ad).join(Competitor)

        if filters.competitor_ids:
            query = query.filter(Ad.competitor_id.in_(filters.competitor_ids))
        if filters.course and filters.course != "All":
            query = query.filter(Competitor.course == filters.course)
        if filters.city:
            query = query.filter(Competitor.city == filters.city)

        if filters.sort_by == "days":
            query = query.order_by(Ad.run_days.desc())
        elif filters.sort_by == "new":
            query = query.order_by(Ad.first_seen.desc())
        else:
            query = query.order_by(Ad.id.asc())

        ads = query.limit(filters.limit).offset(filters.offset).all()
        responses = []

        for ad in ads:
            media_item = ad.media[0] if ad.media else None
            analysis = ad.analysis

            tactics_list = [t.strip() for t in analysis.tactics_str.split(",") if t.strip()] if analysis else []

            responses.append(
                AdResponse(
                    id=ad.id,
                    ad_archive_id=ad.ad_archive_id,
                    competitor_id=ad.competitor_id,
                    competitor_name=ad.competitor.name,
                    course=ad.competitor.course,
                    copy=ad.copy,
                    headline=ad.headline,
                    cta=ad.cta,
                    platforms=ad.platforms_str.split(",") if ad.platforms_str else ["facebook", "instagram"],
                    start_date=ad.start_date,
                    is_active=ad.is_active,
                    first_seen=ad.first_seen,
                    last_seen=ad.last_seen,
                    run_days=ad.run_days,
                    media_url=media_item.storage_path or media_item.original_url if media_item else None,
                    media_type=media_item.media_type if media_item else "image",
                    score=analysis.effectiveness_score if analysis else 70,
                    hook=analysis.hook if analysis else ad.headline,
                    offer=analysis.offer if analysis else "Special demo session",
                    audience=analysis.target_audience if analysis else "Learners in Coimbatore",
                    tactics=tactics_list,
                    why=analysis.why_it_works if analysis else "Direct clear messaging.",
                    weak=analysis.weaknesses if analysis else "Missing public proof.",
                    created_at=ad.created_at,
                )
            )

        # Sort by score if requested
        if filters.sort_by == "score":
            responses.sort(key=lambda x: (x.score or 0), reverse=True)

        return responses

    def collect_ads_for_competitor(self, competitor_id: int) -> int:
        competitor = self.db.query(Competitor).filter(Competitor.id == competitor_id).first()
        if not competitor:
            return 0

        collected_records: List[AdRecord] = []

        # Execute fallback chain
        for provider in self.chain:
            start_t = time.time()
            try:
                records = provider.fetch_ads(page_id=competitor.fb_page_id or competitor.name)
                duration_ms = int((time.time() - start_t) * 1000)

                self._record_scrape_run(
                    provider=provider.name,
                    status="success" if records else "empty",
                    rows=len(records),
                    duration_ms=duration_ms,
                )

                if records:
                    collected_records = records
                    logger.info(f"Provider {provider.name} returned {len(records)} ads for {competitor.name}")
                    break
            except Exception as e:
                duration_ms = int((time.time() - start_t) * 1000)
                self._record_scrape_run(
                    provider=provider.name,
                    status="error",
                    rows=0,
                    duration_ms=duration_ms,
                    error=str(e),
                )
                logger.warning(f"Provider {provider.name} failed: {e}. Falling through to next provider.")

        # Persist and deduplicate by ad_archive_id
        upserted_count = 0
        for rec in collected_records:
            existing = self.db.query(Ad).filter(Ad.ad_archive_id == rec.ad_archive_id).first()
            now = datetime.now(timezone.utc).replace(tzinfo=None)

            if existing:
                existing.last_seen = now
                existing.is_active = rec.is_active
                if existing.first_seen:
                    first_dt = existing.first_seen
                    if hasattr(first_dt, "tzinfo") and first_dt.tzinfo is not None:
                        first_dt = first_dt.replace(tzinfo=None)
                    diff_days = max(1, (now - first_dt).days)
                    existing.run_days = diff_days
                ad_obj = existing
            else:
                raw_days = rec.raw.get("days", 1) if isinstance(rec.raw, dict) else 1
                simulated_first_seen = now - timedelta(days=raw_days)

                ad_obj = Ad(
                    ad_archive_id=rec.ad_archive_id,
                    competitor_id=competitor.id,
                    source=rec.source,
                    copy=rec.copy,
                    headline=rec.headline,
                    cta=rec.cta,
                    platforms_str=",".join(rec.platforms),
                    start_date=rec.start_date,
                    is_active=rec.is_active,
                    first_seen=simulated_first_seen,
                    last_seen=now,
                    run_days=raw_days,
                )
                self.db.add(ad_obj)
                self.db.flush()

            # Save media references
            for m in rec.media:
                media_exist = self.db.query(AdMedia).filter(AdMedia.ad_id == ad_obj.id, AdMedia.original_url == m.url).first()
                if not media_exist:
                    new_media = AdMedia(
                        ad_id=ad_obj.id,
                        media_type=m.type,
                        original_url=m.url,
                        storage_path=m.url,
                    )
                    self.db.add(new_media)

            upserted_count += 1

        self.db.commit()
        return upserted_count

    def refresh_all_competitors(self) -> int:
        competitors = self.db.query(Competitor).filter(Competitor.is_active == True).all()
        total = 0
        for c in competitors:
            total += self.collect_ads_for_competitor(c.id)
        return total

    def _record_scrape_run(self, provider: str, status: str, rows: int, duration_ms: int, error: Optional[str] = None):
        run = ScrapeRun(
            provider=provider,
            status=status,
            rows_collected=rows,
            duration_ms=duration_ms,
            error_message=error,
        )
        self.db.add(run)
        self.db.commit()
