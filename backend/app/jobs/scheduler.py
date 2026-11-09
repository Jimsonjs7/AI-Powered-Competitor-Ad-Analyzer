import argparse
import asyncio
import sys
import time
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.models.ad import Ad
from app.models.competitor import Competitor
from app.services.ad_service import AdService
from app.services.analysis_service import AnalysisService

logger = get_logger("jobs.scheduler")


def run_scrape_and_analysis_cycle(db: Session) -> Dict[str, Any]:
    start_time = time.time()
    competitors = db.query(Competitor).filter(Competitor.is_active == True).all()

    logger.info(f"Starting automated scrape cycle for {len(competitors)} active competitors...")
    ad_service = AdService(db)
    analysis_service = AnalysisService(db)

    total_ads_collected = 0
    total_analyzed = 0

    for comp in competitors:
        try:
            logger.info(f"Scraping ads for competitor #{comp.id}: {comp.name}...")
            collected = ad_service.collect_ads_for_competitor(comp.id)
            total_ads_collected += collected
        except Exception as e:
            logger.error(f"Failed scraping for competitor #{comp.id} ({comp.name}): {e}")

    # Automatically analyze any unanalyzed active ads using Gemini 3-key pool
    unanalyzed_ads = (
        db.query(Ad)
        .filter(Ad.is_active == True)
        .outerjoin(Ad.analysis)
        .filter(Ad.analysis == None)  # noqa: E711
        .all()
    )

    logger.info(f"Found {len(unanalyzed_ads)} unanalyzed ads. Beginning automated AI analysis...")
    for ad in unanalyzed_ads:
        try:
            analysis_service.analyze_ad(ad.id)
            total_analyzed += 1
            # Respect rate limits between calls
            time.sleep(settings.min_seconds_between_requests)
        except Exception as e:
            logger.warning(f"Could not analyze ad #{ad.id} ({e})")

    elapsed_sec = round(time.time() - start_time, 2)
    logger.info(
        f"Automated cycle finished in {elapsed_sec}s: "
        f"{len(competitors)} competitors processed, "
        f"{total_ads_collected} ads collected, "
        f"{total_analyzed} ads analyzed."
    )

    return {
        "status": "completed",
        "competitors_count": len(competitors),
        "ads_collected": total_ads_collected,
        "ads_analyzed": total_analyzed,
        "duration_seconds": elapsed_sec,
    }


async def scheduler_daemon_loop():
    logger.info("Background scraping daemon initialized.")
    interval_seconds = max(300, settings.auto_scrape_interval_hours * 3600)

    while True:
        db = SessionLocal()
        try:
            run_scrape_and_analysis_cycle(db)
        except Exception as e:
            logger.error(f"Error in automated scraping cycle: {e}")
        finally:
            db.close()

        logger.info(f"Sleeping for {interval_seconds}s until next cycle...")
        await asyncio.sleep(interval_seconds)


def main():
    parser = argparse.ArgumentParser(description="Ad Desk Automated Scraping & Analysis Scheduler")
    parser.add_argument("--once", action="store_true", help="Run a single scrape and analysis cycle then exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuous background daemon")
    args = parser.parse_args()

    if args.daemon or (not args.once):
        try:
            asyncio.run(scheduler_daemon_loop())
        except KeyboardInterrupt:
            logger.info("Scheduler daemon stopped by user.")
            sys.exit(0)
    else:
        db = SessionLocal()
        try:
            res = run_scrape_and_analysis_cycle(db)
            print(f"Cycle completed successfully: {res}")
        finally:
            db.close()


if __name__ == "__main__":
    main()
