from sqlalchemy.orm import Session
from app.models.scrape_run import ScrapeRun
from app.schemas.scrape_run import HealthStatusResponse


class HealthService:
    def __init__(self, db: Session):
        self.db = db

    def check_providers(self) -> HealthStatusResponse:
        providers = ["apify_meta_primary", "scrapecreators_ads", "playwright_adlibrary"]
        provider_health = {}
        active_count = 0

        for p in providers:
            last_run = (
                self.db.query(ScrapeRun)
                .filter(ScrapeRun.provider == p)
                .order_by(ScrapeRun.created_at.desc())
                .first()
            )
            is_ok = True
            if last_run and last_run.status == "error":
                is_ok = False

            provider_health[p] = {
                "ok": is_ok,
                "last_run": last_run.created_at.isoformat() if last_run else None,
            }
            if is_ok:
                active_count += 1

        total = len(providers)
        if active_count == total:
            message = "All 3 ad sources responding"
        else:
            message = f"{active_count} of {total} ad sources responding"

        return HealthStatusResponse(
            status="ok" if active_count > 0 else "degraded",
            active_providers_count=active_count,
            total_providers_count=total,
            message=message,
            providers_health=provider_health,
        )

