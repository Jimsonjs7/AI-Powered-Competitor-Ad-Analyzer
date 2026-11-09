import httpx
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.providers.ads.base import AdSource
from app.schemas.ad import AdRecord, MediaItem

logger = get_logger("provider.scrapecreators")


class ScrapeCreatorsProvider(AdSource):
    name = "scrapecreators_ads"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.scrapecreators_api_key

    def fetch_ads(
        self,
        *,
        page_id: Optional[str] = None,
        keyword: Optional[str] = None,
        country: str = "IN",
        status: str = "active",
        limit: int = 100,
    ) -> List[AdRecord]:
        if not self.api_key:
            logger.info("ScrapeCreators API key not set, skipping provider.")
            return []

        url = "https://api.scrapecreators.com/v1/meta/company/ads"
        params = {
            "page_id": page_id,
            "country": country,
            "status": status,
            "limit": limit,
        }

        try:
            with httpx.Client(timeout=settings.scrape_timeout_seconds) as client:
                response = client.get(
                    url,
                    headers={"x-api-key": self.api_key},
                    params=params,
                )
                if response.status_code != 200:
                    logger.error(f"ScrapeCreators request failed: {response.status_code}")
                    return []

                data = response.json()
                items = data.get("ads") or []
                return [self._normalize(item) for item in items]
        except Exception as e:
            logger.error(f"ScrapeCreators call failed: {e}")
            raise e

    def _normalize(self, raw: Dict[str, Any]) -> AdRecord:
        media_items = []
        if raw.get("image_url"):
            media_items.append(MediaItem(type="image", url=raw["image_url"]))
        if raw.get("video_url"):
            media_items.append(MediaItem(type="video", url=raw["video_url"]))

        return AdRecord(
            ad_archive_id=str(raw.get("ad_id") or raw.get("id")),
            page_id=str(raw.get("page_id") or ""),
            page_name=str(raw.get("page_name") or "Competitor"),
            source=self.name,
            copy=str(raw.get("caption") or raw.get("copy") or ""),
            headline=raw.get("headline"),
            cta=raw.get("cta_title"),
            platforms=raw.get("platforms") or ["facebook", "instagram"],
            start_date=raw.get("first_seen_date"),
            is_active=raw.get("is_active", True),
            media=media_items,
            raw=raw,
        )
