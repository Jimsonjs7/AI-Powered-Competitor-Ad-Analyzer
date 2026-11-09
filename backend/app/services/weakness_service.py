import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import get_logger
from app.models.ad import Ad
from app.models.competitor import Competitor
from app.models.competitor_metrics import CompetitorMetrics
from app.models.evidence import EvidenceItem
from app.models.weakness import Weakness
from app.providers.llm.gemini_client import GeminiLLMClient
from app.schemas.weakness import DataSufficiencyResponse, WeaknessListResponse, WeaknessResponse

logger = get_logger("service.weakness")

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


class WeaknessService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = GeminiLLMClient()

    def check_data_sufficiency(self, competitor_id: int, thresholds: Optional[Dict[str, int]] = None) -> DataSufficiencyResponse:
        t = thresholds or {"min_ads": 3, "min_reviews": 20, "min_comments": 15}

        ads_count = self.db.query(Ad).filter(Ad.competitor_id == competitor_id, Ad.is_active == True).count()

        counts_rows = (
            self.db.query(EvidenceItem.source, func.count(EvidenceItem.id))
            .filter(EvidenceItem.competitor_id == competitor_id)
            .group_by(EvidenceItem.source)
            .all()
        )
        counts = {r[0]: r[1] for r in counts_rows}
        reviews_count = counts.get("google_maps", 0)
        comments_count = counts.get("fb_comments", 0) + counts.get("manual", 0)

        is_sufficient = (
            ads_count >= t["min_ads"]
            or reviews_count >= t["min_reviews"]
            or comments_count >= t["min_comments"]
        )

        missing = []
        if ads_count < t["min_ads"]:
            missing.append(f"Need {t['min_ads']} active ads (have {ads_count})")
        if reviews_count < t["min_reviews"] and comments_count < t["min_comments"]:
            missing.append(
                f"Need {t['min_reviews']} reviews or {t['min_comments']} comments (have {reviews_count} reviews, {comments_count} comments)"
            )

        return DataSufficiencyResponse(
            competitor_id=competitor_id,
            ads_count=ads_count,
            reviews_count=reviews_count,
            comments_count=comments_count,
            is_sufficient=is_sufficient,
            missing=missing,
        )

    def analyze_competitor(self, competitor_id: int) -> List[WeaknessResponse]:
        competitor = self.db.query(Competitor).filter(Competitor.id == competitor_id).first()
        if not competitor:
            raise ValueError(f"Competitor {competitor_id} not found.")

        # Data sufficiency check
        sufficiency = self.check_data_sufficiency(competitor_id)
        if not sufficiency.is_sufficient:
            # If insufficient data, return existing or empty without fabricating analysis
            return self.list_weaknesses_for_competitor(competitor_id).weaknesses

        # Fetch evidence items
        evidence_items = self.db.query(EvidenceItem).filter(EvidenceItem.competitor_id == competitor_id).all()
        ads = self.db.query(Ad).filter(Ad.competitor_id == competitor_id, Ad.is_active == True).all()

        total_sample = len(evidence_items) + len(ads)

        # Categorize evidence counts
        category_counts: Dict[str, int] = {}
        category_samples: Dict[str, List[str]] = {}

        # 1. Analyze ad copy gaps
        for ad in ads:
            copy_lower = (ad.copy or "").lower()
            if not any(kw in copy_lower for kw in ["₹", "fee", "cost", "price", "emi"]):
                category_counts["pricing_clarity"] = category_counts.get("pricing_clarity", 0) + 1
                category_samples.setdefault("pricing_clarity", []).append("Ad copy does not disclose fees or payment options.")
            if not any(kw in copy_lower for kw in ["placed", "hired", "salary", "alumni", "partner"]):
                category_counts["placement_claims"] = category_counts.get("placement_claims", 0) + 1
                category_samples.setdefault("placement_claims", []).append("Ad copy makes vague promises without verifiable placement proof.")
            if not any(kw in copy_lower for kw in ["batch", "starts", "schedule", "timing", "weekend", "weekday"]):
                category_counts["schedule_clarity"] = category_counts.get("schedule_clarity", 0) + 1
                category_samples.setdefault("schedule_clarity", []).append("Ad lacks clear batch start date or schedule options.")

        # 2. Analyze collected comments/reviews
        for ev in evidence_items:
            cat = ev.category if ev.category in CATEGORIES else "other"
            category_counts[cat] = category_counts.get(cat, 0) + 1
            category_samples.setdefault(cat, []).append(ev.text[:120])

        # Delete existing weaknesses before regenerating
        self.db.query(Weakness).filter(Weakness.competitor_id == competitor_id).delete()

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        saved_weaknesses = []
        total_weighted_severity = 0.0

        for cat, count in category_counts.items():
            sample_size = total_sample
            share_pct = round((count / max(1, sample_size)) * 100, 1)
            confidence = "high" if count >= 15 else ("medium" if count >= 5 else "low")
            severity = 4 if cat in ("pricing_clarity", "placement_claims") else (3 if cat == "schedule_clarity" else 2)

            samples_snippet = " | ".join(category_samples.get(cat, [])[:3])
            summary = self._generate_summary(competitor.name, cat, count, share_pct, samples_snippet)

            w = Weakness(
                competitor_id=competitor_id,
                category=cat,
                summary=summary,
                evidence_count=count,
                sample_size=sample_size,
                share_percent=share_pct,
                confidence=confidence,
                severity=severity,
                computed_at=now,
            )
            self.db.add(w)
            saved_weaknesses.append(w)
            total_weighted_severity += severity * count

        # Update CompetitorMetrics and Competitor status
        metrics = competitor.metrics
        if not metrics:
            metrics = CompetitorMetrics(competitor_id=competitor_id)
            self.db.add(metrics)

        metrics.weakness_score = round(min(100.0, total_weighted_severity * 1.5), 1)
        metrics.threat_score = round(max(20.0, 100.0 - metrics.weakness_score * 0.5), 1)
        metrics.computed_at = now
        competitor.data_status = "analyzed"

        self.db.commit()

        return [
            WeaknessResponse(
                id=w.id,
                competitor_id=w.competitor_id,
                category=w.category,
                summary=w.summary,
                evidence_count=w.evidence_count,
                sample_size=w.sample_size,
                share_percent=w.share_percent,
                confidence=w.confidence,
                severity=w.severity,
                computed_at=w.computed_at,
            )
            for w in saved_weaknesses
        ]

    def _generate_summary(self, comp_name: str, category: str, count: int, share_pct: float, samples: str) -> str:
        cat_human = category.replace("_", " ")
        if category == "pricing_clarity":
            return f"Fees are not disclosed in {count} creatives ({share_pct}% share); prospects frequently question actual pricing."
        elif category == "placement_claims":
            return f"Claims outcome results in {count} ads ({share_pct}% share) without mentioning hiring partners or verifiable proofs."
        elif category == "schedule_clarity":
            return f"Batch schedules and timing are omitted in {count} ads ({share_pct}% share), creating hesitation for working learners."
        return f"{comp_name} exhibits {cat_human} gaps across {count} evidence items ({share_pct}% share)."

    def list_weaknesses_for_competitor(self, competitor_id: int) -> WeaknessListResponse:
        competitor = self.db.query(Competitor).filter(Competitor.id == competitor_id).first()
        status = competitor.data_status if competitor else "pending"

        weaknesses = (
            self.db.query(Weakness)
            .filter(Weakness.competitor_id == competitor_id)
            .order_by(Weakness.severity.desc(), Weakness.evidence_count.desc())
            .all()
        )
        total_ev = self.db.query(EvidenceItem).filter(EvidenceItem.competitor_id == competitor_id).count()
        sufficiency = self.check_data_sufficiency(competitor_id)

        responses = [
            WeaknessResponse(
                id=w.id,
                competitor_id=w.competitor_id,
                category=w.category,
                summary=w.summary,
                evidence_count=w.evidence_count,
                sample_size=w.sample_size,
                share_percent=w.share_percent,
                confidence=w.confidence,
                severity=w.severity,
                computed_at=w.computed_at,
            )
            for w in weaknesses
        ]

        latest = weaknesses[0].computed_at if weaknesses else None

        return WeaknessListResponse(
            competitor_id=competitor_id,
            weaknesses=responses,
            data_status=status,
            total_evidence=total_ev,
            is_sufficient=sufficiency.is_sufficient,
            analyzed_at=latest,
        )

