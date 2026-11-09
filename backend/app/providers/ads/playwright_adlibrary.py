from typing import List, Optional
from app.core.logging import get_logger
from app.providers.ads.base import AdSource
from app.schemas.ad import AdRecord

logger = get_logger("provider.playwright")


class PlaywrightAdLibraryProvider(AdSource):
    name = "playwright_adlibrary"

    def fetch_ads(
        self,
        *,
        page_id: Optional[str] = None,
        keyword: Optional[str] = None,
        country: str = "IN",
        status: str = "active",
        limit: int = 100,
    ) -> List[AdRecord]:
        logger.info(f"Playwright fallback invoked for page_id: {page_id}")
        # Graceful fallback when headless browser is not active
        return []

