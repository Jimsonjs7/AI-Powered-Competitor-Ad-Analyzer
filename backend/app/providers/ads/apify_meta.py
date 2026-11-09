import httpx
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.providers.ads.base import AdSource
from app.schemas.ad import AdRecord, MediaItem

logger = get_logger("provider.apify_meta")


class ApifyMetaProvider(AdSource):
    name = "apify_meta_primary"

    def __init__(self, token: Optional[str] = None, actor_id: Optional[str] = None):
        self.token = token or settings.apify_api_token
        self.actor_id = actor_id or settings.apify_meta_actor_id

    def fetch_ads(
        self,
        *,
        page_id: Optional[str] = None,
        keyword: Optional[str] = None,
        country: str = "IN",
        status: str = "active",
        limit: int = 100,
    ) -> List[AdRecord]:
        if not self.token:
            logger.info("Apify API token not set, skipping provider.")
            return []

        url = f"https://api.apify.com/v2/acts/{self.actor_id}/run-sync-get-dataset-items"
        run_input = {
            "pageIds": [page_id] if page_id else [],
            "searchQuery": keyword or "",
            "country": country,
            "activeStatus": status,
            "maxAds": limit,
        }

        try:
            with httpx.Client(timeout=settings.scrape_timeout_seconds) as client:
                response = client.post(
                    url,
                    headers={"Authorization": f"Bearer {self.token}"},
                    json=run_input,
                )
                if response.status_code != 200:
                    logger.error(f"Apify request failed with status: {response.status_code}")
                    return []

                raw_items = response.json()
                return [self._normalize(item) for item in raw_items if isinstance(item, dict)]
        except Exception as e:
            logger.error(f"Apify meta provider call failed: {e}")
            raise e

    def _normalize(self, raw: Dict[str, Any]) -> AdRecord:
        archive_id = str(raw.get("id") or raw.get("ad_archive_id") or raw.get("adArchiveID") or "")
        page_id = str(raw.get("page_id") or raw.get("pageId") or "")
        page_name = str(raw.get("page_name") or raw.get("pageName") or "Competitor")

        # Extract creative media links
        media_items: List[MediaItem] = []
        images = raw.get("images") or raw.get("snapshot", {}).get("images") or []
        for img in images:
            img_url = img if isinstance(img, str) else img.get("url") or img.get("original_image_url")
            if img_url:
                media_items.append(MediaItem(type="image", url=str(img_url)))

        videos = raw.get("videos") or raw.get("snapshot", {}).get("videos") or []
        for vid in videos:
            vid_url = vid if isinstance(vid, str) else vid.get("url") or vid.get("video_sd_url")
            if vid_url:
                media_items.append(MediaItem(type="video", url=str(vid_url)))

        copy_text = raw.get("body") or raw.get("copy") or raw.get("snapshot", {}).get("body", {}).get("text") or ""
        headline_text = raw.get("title") or raw.get("headline") or raw.get("snapshot", {}).get("title")
        cta_text = raw.get("cta_text") or raw.get("cta") or raw.get("snapshot", {}).get("cta_text")

        return AdRecord(
            ad_archive_id=archive_id,
            page_id=page_id,
            page_name=page_name,
            source=self.name,
            copy=str(copy_text),
            headline=str(headline_text) if headline_text else None,
            cta=str(cta_text) if cta_text else None,
            platforms=raw.get("publisher_platforms") or ["facebook", "instagram"],
            start_date=raw.get("start_date") or raw.get("startDate"),
            is_active=True,
            media=media_items,
            raw=raw,
        )
