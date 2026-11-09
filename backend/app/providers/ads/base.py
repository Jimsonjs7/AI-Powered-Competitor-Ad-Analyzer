from typing import List, Optional, Protocol
from app.schemas.ad import AdRecord


class AdSource(Protocol):
    name: str

    def fetch_ads(
        self,
        *,
        page_id: Optional[str] = None,
        keyword: Optional[str] = None,
        country: str = "IN",
        status: str = "active",
        limit: int = 100,
    ) -> List[AdRecord]:
        """Fetch and return normalised AdRecord list from target ad provider."""
        ...

