import httpx
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from app.core.config import settings
from app.core.logging import get_logger
from app.providers.ads.base import AdSource
from app.schemas.ad import AdRecord, MediaItem

logger = get_logger("provider.apify_meta")


class ApifyMetaProvider(AdSource):
    name = "apify_meta_primary"

    def __init__(self, tokens: Optional[List[str]] = None, actor_id: Optional[str] = None):
        self.tokens = tokens or settings.all_apify_api_tokens
        configured_actor = (actor_id or settings.apify_meta_actor_id or "").strip()
        self.actor_id = configured_actor if configured_actor else "jaybird~meta-ad-library-scraper"

    def fetch_ads(
        self,
        *,
        page_id: Optional[str] = None,
        keyword: Optional[str] = None,
        country: str = "IN",
        status: str = "active",
        limit: int = 30,
    ) -> List[AdRecord]:
        tokens_pool = self.tokens or settings.all_apify_api_tokens
        if not tokens_pool:
            logger.info("Apify API tokens not configured, skipping provider.")
            return []

        formatted_actor_id = self.actor_id.replace("/", "~")
        url = f"https://api.apify.com/v2/acts/{formatted_actor_id}/run-sync-get-dataset-items?timeout=30"

        # Determine optimal lookup mode for jaybird/meta-ad-library-scraper
        search_target = page_id or keyword or ""
        run_input: Dict[str, Any] = {
            "region": country,
            "active_only": (status == "active"),
            "max_ads_per_advertiser": limit,
            "media_type": "all",
        }

        if search_target.isdigit():
            run_input["search_mode"] = "page_id"
            run_input["page_id"] = search_target
        elif "facebook.com" in search_target or "fb.com" in search_target:
            run_input["search_mode"] = "page_url"
            run_input["page_url"] = search_target
        elif search_target.startswith("page_") and not search_target[5:].isdigit():
            # Clean slug to keyword search
            clean_kw = search_target[5:].replace("_", " ").title()
            run_input["search_mode"] = "keyword"
            run_input["query"] = clean_kw
        else:
            run_input["search_mode"] = "keyword"
            run_input["query"] = search_target

        # Iterate through token failover pool
        for idx, token in enumerate(tokens_pool):
            try:
                with httpx.Client(timeout=settings.scrape_timeout_seconds) as client:
                    response = client.post(
                        url,
                        headers={"Authorization": f"Bearer {token}"},
                        json=run_input,
                    )

                    if response.status_code == 200:
                        raw_items = response.json()
                        records = [self._normalize(item) for item in raw_items if isinstance(item, dict) and not item.get("no_ads_found")]
                        logger.info(f"Apify token #{idx + 1} succeeded: {len(records)} ads collected.")
                        return records

                    elif response.status_code == 201:
                        # Asynchronous execution started: poll run status until completion
                        data = response.json()
                        data_obj = data.get("data") if isinstance(data, dict) and isinstance(data.get("data"), dict) else data
                        run_id = data_obj.get("id") if isinstance(data_obj, dict) else None
                        dataset_id = data_obj.get("defaultDatasetId") if isinstance(data_obj, dict) else None
                        if run_id and dataset_id:
                            records = self._poll_run_results(client, token, run_id, dataset_id)
                            if records is not None:
                                logger.info(f"Apify run #{run_id} completed: {len(records)} ads collected.")
                                return records

                    logger.warning(
                        f"Apify token #{idx + 1} returned status {response.status_code}. Failing over to next token..."
                    )
            except Exception as e:
                logger.warning(
                    f"Apify token #{idx + 1} call error ({e}). Failing over to next token in pool..."
                )

        logger.info("All configured Apify tokens exhausted or returned no records.")
        return []

    def _poll_run_results(
        self, client: httpx.Client, token: str, run_id: str, dataset_id: str, max_wait_sec: int = 30
    ) -> Optional[List[AdRecord]]:
        start_wait = time.time()
        while time.time() - start_wait < max_wait_sec:
            time.sleep(3)
            try:
                run_res = client.get(
                    f"https://api.apify.com/v2/actor-runs/{run_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                if run_res.status_code == 200:
                    status = run_res.json().get("data", {}).get("status")
                    if status in ("SUCCEEDED", "ABORTED"):
                        # Fetch dataset items
                        ds_res = client.get(
                            f"https://api.apify.com/v2/datasets/{dataset_id}/items",
                            headers={"Authorization": f"Bearer {token}"},
                        )
                        if ds_res.status_code == 200:
                            raw_items = ds_res.json()
                            return [
                                self._normalize(item)
                                for item in raw_items
                                if isinstance(item, dict) and not item.get("no_ads_found")
                            ]
                        return []
                    elif status in ("FAILED", "TIMED-OUT"):
                        return None
            except Exception:
                pass
        return None

    def _normalize(self, raw: Dict[str, Any]) -> AdRecord:
        archive_id = str(
            raw.get("ad_archive_id")
            or raw.get("id")
            or raw.get("adArchiveID")
            or f"meta_{int(time.time() * 1000)}"
        )
        page_id = str(raw.get("page_id") or raw.get("pageId") or "")
        page_name = str(raw.get("page_name") or raw.get("pageName") or "Competitor")

        # Collect media items (supporting jaybird schema and generic schemas)
        media_items: List[MediaItem] = []

        all_images = raw.get("all_image_urls") or []
        if isinstance(all_images, list):
            for img in all_images:
                if img and isinstance(img, str):
                    media_items.append(MediaItem(type="image", url=img))

        single_img = raw.get("image_url")
        if single_img and isinstance(single_img, str) and not any(m.url == single_img for m in media_items):
            media_items.append(MediaItem(type="image", url=single_img))

        all_videos = raw.get("all_video_urls") or []
        if isinstance(all_videos, list):
            for vid in all_videos:
                if vid and isinstance(vid, str):
                    media_items.append(MediaItem(type="video", url=vid))

        single_vid = raw.get("video_url")
        if single_vid and isinstance(single_vid, str) and not any(m.url == single_vid for m in media_items):
            media_items.append(MediaItem(type="video", url=single_vid))

        # Fallback to snapshot parsing if present
        snap = raw.get("snapshot")
        snap_obj = snap[0] if isinstance(snap, list) and len(snap) > 0 and isinstance(snap[0], dict) else (snap if isinstance(snap, dict) else {})

        if not media_items:
            images = raw.get("images") or snap_obj.get("images") or []
            if isinstance(images, list):
                for img in images:
                    u = img if isinstance(img, str) else (img.get("url") or img.get("original_image_url") if isinstance(img, dict) else None)
                    if u:
                        media_items.append(MediaItem(type="image", url=str(u)))

        snap_body = snap_obj.get("body")
        snap_body_text = snap_body.get("text") if isinstance(snap_body, dict) else (snap_body if isinstance(snap_body, str) else "")

        copy_text = (
            raw.get("body_text")
            or raw.get("body")
            or raw.get("copy")
            or raw.get("caption")
            or snap_body_text
            or ""
        )
        headline_text = raw.get("title") or raw.get("headline") or snap_obj.get("title")
        cta_text = raw.get("cta_text") or raw.get("cta") or snap_obj.get("cta_text")

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
            is_active=raw.get("is_active", True),
            media=media_items,
            raw=raw,
        )
