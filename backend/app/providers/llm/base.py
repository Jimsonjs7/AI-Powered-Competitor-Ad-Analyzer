from typing import Any, Dict, List, Optional, Protocol
from app.schemas.analysis import AdAnalysisSchema


class LLMClient(Protocol):
    name: str

    def analyze(
        self,
        *,
        images: List[str],
        copy_text: str,
        headline: Optional[str] = None,
        cta: Optional[str] = None,
        running_days: int = 1,
    ) -> AdAnalysisSchema:
        """Execute multimodal strategic analysis and return validated AdAnalysisSchema."""
        ...

