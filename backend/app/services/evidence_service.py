import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.core.security import sanitize_text
from app.models.evidence import EvidenceItem
from app.schemas.evidence import EvidenceItemResponse, EvidenceListResponse

logger = get_logger("service.evidence")

RETENTION_DAYS = 90
CATEGORIES = [
    "pricing_clarity",
    "trust_proof",
    "placement_claims",
    "schedule_clarity",
    "teaching_quality",
    "student_support",
    "location_access",
    "course_relevance",
    "refund_terms",
    "other",
]


class EvidenceService:
    def __init__(self, db: Session):
        self.db = db

    def add_evidence(
        self,
        competitor_id: int,
        source: str,
        text: str,
        category: Optional[str] = None,
        ad_id: Optional[int] = None,
    ) -> EvidenceItem:
        clean = sanitize_text(text)
        if not clean:
            raise ValueError("Evidence text cannot be empty after sanitization.")

        # Privacy strip: remove usernames (@user), phone numbers, URLs, and profile references
        clean = re.sub(r"@[\w\.-]+", "[user]", clean)
        clean = re.sub(r"https?://\S+", "[link]", clean)
        clean = re.sub(r"\b\d{10}\b", "[phone]", clean)

        # Deduplicate using one-way SHA-256
        text_hash = hashlib.sha256(clean.encode()).hexdigest()
        existing = (
            self.db.query(EvidenceItem)
            .filter(EvidenceItem.competitor_id == competitor_id, EvidenceItem.text_hash == text_hash)
            .first()
        )
        if existing:
            return existing

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        item = EvidenceItem(
            competitor_id=competitor_id,
            ad_id=ad_id,
            source=source,
            text_hash=text_hash,
            text=clean,
            category=category or "other",
            collected_at=now,
            expires_at=now + timedelta(days=RETENTION_DAYS),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_evidence_for_competitor(
        self, competitor_id: int, page: int = 1, page_size: int = 50
    ) -> EvidenceListResponse:
        query = self.db.query(EvidenceItem).filter(EvidenceItem.competitor_id == competitor_id)
        total = query.count()
        items = query.order_by(EvidenceItem.collected_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        # Breakdown by source
        breakdown_rows = (
            self.db.query(EvidenceItem.source, func.count(EvidenceItem.id))
            .filter(EvidenceItem.competitor_id == competitor_id)
            .group_by(EvidenceItem.source)
            .all()
        )
        source_breakdown = {row[0]: row[1] for row in breakdown_rows}

        responses = [
            EvidenceItemResponse(
                id=item.id,
                competitor_id=item.competitor_id,
                ad_id=item.ad_id,
                source=item.source,
                text=item.text,
                language=item.language,
                sentiment=item.sentiment,
                category=item.category,
                collected_at=item.collected_at,
            )
            for item in items
        ]

        return EvidenceListResponse(
            competitor_id=competitor_id,
            items=responses,
            total=total,
            source_breakdown=source_breakdown,
        )

    def get_counts_for_competitor(self, competitor_id: int) -> Dict[str, int]:
        rows = (
            self.db.query(EvidenceItem.source, func.count(EvidenceItem.id))
            .filter(EvidenceItem.competitor_id == competitor_id)
            .group_by(EvidenceItem.source)
            .all()
        )
        return {row[0]: row[1] for row in rows}

    def purge_expired(self) -> int:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        count = self.db.query(EvidenceItem).filter(EvidenceItem.expires_at < now).delete()
        self.db.commit()
        return count

