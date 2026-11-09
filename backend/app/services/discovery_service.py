import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.models.competitor import Competitor
from app.models.competitor_metrics import CompetitorMetrics
from app.models.discovery import DiscoveryRun
from app.models.profile import BusinessProfile
from app.providers.ads.apify_meta import ApifyMetaProvider
from app.services.ad_service import AdService
from app.services.competitor_service import CompetitorService

logger = get_logger("service.discovery")


class DiscoveryService:
    def __init__(self, db: Session):
        self.db = db

    def create_run(self, radius_km: float = 10.0, search_terms: Optional[List[str]] = None) -> DiscoveryRun:
        profile = (
            self.db.query(BusinessProfile)
            .filter(BusinessProfile.is_active == True)
            .order_by(BusinessProfile.id.desc())
            .first()
        )
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        run = DiscoveryRun(
            profile_id=profile.id if profile else None,
            status="pending",
            current_step="Created",
            radius_km=radius_km,
            filters_json=json.dumps({"search_terms": search_terms or []}),
            providers_json=json.dumps(["apify_meta_primary", "local_directory"]),
            counts_json=json.dumps({"places_found": 0, "pages_resolved": 0, "ads_collected": 0}),
            started_at=now,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get_run_status(self, run_id: int) -> Optional[DiscoveryRun]:
        return self.db.query(DiscoveryRun).filter(DiscoveryRun.id == run_id).first()

    def cancel_run(self, run_id: int) -> bool:
        run = self.get_run_status(run_id)
        if run and run.status in ("pending", "running"):
            run.status = "cancelled"
            run.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
            self.db.commit()
            return True
        return False

    @staticmethod
    async def execute_discovery_async(run_id: int, city: str, search_terms: List[str]):
        """Runs in background task with a fresh database session."""
        db = SessionLocal()
        try:
            run = db.query(DiscoveryRun).filter(DiscoveryRun.id == run_id).first()
            if not run or run.status == "cancelled":
                return

            run.status = "running"
            run.current_step = f"Building search queries for {city}..."
            db.commit()

            comp_service = CompetitorService(db)
            ad_service = AdService(db)
            places_found = 0
            pages_resolved = 0
            ads_collected = 0

            # Step 1: Discover / collect places
            run.current_step = "Searching institutes and Ad Library advertisers..."
            db.commit()

            terms = search_terms or ["AI Training Institute", "Digital Marketing Course", "UI UX School"]
            discovered_competitors: List[Competitor] = []

            for term in terms:
                if run.status == "cancelled":
                    return

                # Search Ad Library for active advertisers in this niche
                apify_provider = ApifyMetaProvider()
                records = apify_provider.fetch_ads(keyword=f"{term} {city}", limit=10)

                for rec in records:
                    if rec.page_name and rec.page_name != "Competitor":
                        places_found += 1
                        # Resolve and save competitor
                        comp = db.query(Competitor).filter(Competitor.name == rec.page_name).first()
                        if not comp:
                            comp = Competitor(
                                name=rec.page_name,
                                city=city,
                                course="AI" if "ai" in term.lower() else ("UI/UX" if "ui" in term.lower() else "Digital marketing"),
                                fb_page_id=rec.page_id,
                                confidence="high",
                                is_active=True,
                                data_status="has_ads",
                            )
                            db.add(comp)
                            db.flush()
                            db.add(CompetitorMetrics(competitor_id=comp.id))
                            pages_resolved += 1
                            discovered_competitors.append(comp)

                # Update progress
                run.counts_json = json.dumps(
                    {"places_found": places_found, "pages_resolved": pages_resolved, "ads_collected": ads_collected}
                )
                db.commit()

            # Step 2: Collect ads for discovered competitors
            run.current_step = "Collecting active creatives from resolved pages..."
            db.commit()

            # Ensure all competitors have metrics
            all_comps = db.query(Competitor).filter(Competitor.city.ilike(f"%{city}%")).all()
            for c in all_comps:
                if not c.metrics:
                    m = CompetitorMetrics(
                        competitor_id=c.id,
                        active_ads=len([a for a in c.ads if a.is_active]),
                        computed_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    )
                    db.add(m)
                else:
                    c.metrics.active_ads = len([a for a in c.ads if a.is_active])
                    c.metrics.computed_at = datetime.now(timezone.utc).replace(tzinfo=None)

            db.commit()

            for comp in discovered_competitors:
                try:
                    count = ad_service.collect_ads_for_competitor(comp.id)
                    ads_collected += count
                except Exception as e:
                    logger.warning(f"Failed ad collection for {comp.name}: {e}")

            now = datetime.now(timezone.utc).replace(tzinfo=None)
            run.status = "completed"
            run.current_step = f"Completed: {places_found} candidates, {pages_resolved} added, {ads_collected} ads collected."
            run.counts_json = json.dumps(
                {"places_found": places_found, "pages_resolved": pages_resolved, "ads_collected": ads_collected}
            )
            run.finished_at = now
            db.commit()

        except Exception as e:
            logger.error(f"Discovery run #{run_id} failed: {e}")
            run = db.query(DiscoveryRun).filter(DiscoveryRun.id == run_id).first()
            if run:
                run.status = "failed"
                run.current_step = f"Error: {str(e)[:180]}"
                run.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
                db.commit()
        finally:
            db.close()

