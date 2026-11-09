import hashlib
from typing import List, Optional
from app.core.security import validate_target_url
from app.providers.ads.base import AdSource
from app.schemas.ad import AdRecord, MediaItem


class ManualImportProvider(AdSource):
    name = "manual_import"

    def fetch_ads(
        self,
        *,
        page_id: Optional[str] = None,
        keyword: Optional[str] = None,
        country: str = "IN",
        status: str = "active",
        limit: int = 100,
    ) -> List[AdRecord]:
        return []

    def import_from_url(
        self,
        *,
        ad_url: str,
        page_name: str = "Imported Competitor",
        copy_text: str = "",
        headline: Optional[str] = None,
    ) -> AdRecord:
        safe_url = validate_target_url(ad_url)
        url_hash = hashlib.sha256(safe_url.encode()).hexdigest()[:12]
        archive_id = f"manual_{url_hash}"

        return AdRecord(
            ad_archive_id=archive_id,
            page_id="manual_page",
            page_name=page_name,
            source=self.name,
            copy=copy_text,
            headline=headline or "Imported ad creative",
            cta="Learn more",
            platforms=["facebook", "instagram"],
            is_active=True,
            media=[MediaItem(type="image", url=safe_url)],
            raw={"imported_url": safe_url},
        )
