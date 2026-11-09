import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.models.opportunity import ObjectionCluster, Opportunity
from app.models.profile import BusinessProfile, ProfileClaim
from app.models.weakness import Weakness
from app.schemas.opportunity import (
    ObjectionClusterResponse,
    OpportunityDraftResponse,
    OpportunityResponse,
)

logger = get_logger("service.opportunity")


class OpportunityService:
    def __init__(self, db: Session):
        self.db = db

    def build_clusters(self) -> List[ObjectionCluster]:
        # Group weaknesses across competitors by category
        rows = (
            self.db.query(
                Weakness.category,
                func.sum(Weakness.evidence_count),
                func.count(func.distinct(Weakness.competitor_id)),
                func.avg(Weakness.severity),
            )
            .group_by(Weakness.category)
            .all()
        )

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        clusters = []

        for category, total_count, comp_count, avg_sev in rows:
            label = self._label_for_category(category)
            intensity = round(float(total_count or 0) * float(avg_sev or 1) * (1.0 + (comp_count or 1) * 0.25), 1)

            existing = self.db.query(ObjectionCluster).filter(ObjectionCluster.category == category).first()
            if existing:
                existing.total_count = int(total_count or 0)
                existing.competitor_count = int(comp_count or 0)
                existing.intensity = intensity
                existing.label = label
                clusters.append(existing)
            else:
                cluster = ObjectionCluster(
                    label=label,
                    category=category,
                    total_count=int(total_count or 0),
                    competitor_count=int(comp_count or 0),
                    intensity=intensity,
                    created_at=now,
                )
                self.db.add(cluster)
                clusters.append(cluster)

        self.db.commit()
        return clusters

    def _label_for_category(self, category: str) -> str:
        labels = {
            "pricing_clarity": "Unclear course fees and unexpected add-on costs",
            "placement_claims": "Doubts around real placement statistics and hiring partners",
            "schedule_clarity": "Inflexible batch timings and unannounced schedule delays",
            "trust_proof": "Lack of genuine mentor credentials and real student reviews",
            "teaching_quality": "Superficial theory without hands-on project reviews",
            "student_support": "Slow mentor response time during practical labs",
        }
        return labels.get(category, f"Market doubts around {category.replace('_', ' ')}")

    def score_opportunities(self) -> List[OpportunityResponse]:
        clusters = self.build_clusters()
        profile = (
            self.db.query(BusinessProfile)
            .filter(BusinessProfile.is_active == True)
            .order_by(BusinessProfile.id.desc())
            .first()
        )

        approved_claims = (
            [c.text for c in profile.claims if c.approved]
            if profile and profile.claims
            else []
        )

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        opportunities = []

        for cluster in clusters:
            score = round(cluster.intensity * 1.2, 1)
            counter_angle = self._build_counter_angle(cluster.category, profile)
            formats = ["static_poster", "carousel", "faq_ad"]

            headlines = [
                f"{cluster.label}? Full details upfront at {profile.name if profile else 'BrandMonk'}",
                f"Tired of vague claims? Here is exactly what you get",
                f"Clear fees. Live mentors. Zero guesswork.",
            ]

            missing_proofs = []
            if cluster.category == "pricing_clarity" and not any("fee" in c.lower() or "₹" in c for c in approved_claims):
                missing_proofs.append("Add verified fee structure in approved claims to draft price-led ads.")
            if cluster.category == "placement_claims" and not any("placement" in c.lower() or "hired" in c.lower() for c in approved_claims):
                missing_proofs.append("Add placement records or partner list in approved claims to draft outcome-led ads.")

            existing_opp = self.db.query(Opportunity).filter(Opportunity.cluster_id == cluster.id).first()
            if existing_opp:
                existing_opp.score = score
                existing_opp.counter_angle = counter_angle
                existing_opp.formats_json = json.dumps(formats)
                existing_opp.headlines_json = json.dumps(headlines)
                existing_opp.missing_proof_json = json.dumps(missing_proofs)
                opp_record = existing_opp
            else:
                opp_record = Opportunity(
                    cluster_id=cluster.id,
                    score=score,
                    counter_angle=counter_angle,
                    formats_json=json.dumps(formats),
                    headlines_json=json.dumps(headlines),
                    primary_text=f"Unlike other institutes, we provide 100% upfront clarity on your curriculum, schedule, and fees.",
                    missing_proof_json=json.dumps(missing_proofs),
                    status="draft",
                    created_at=now,
                )
                self.db.add(opp_record)

            opportunities.append((opp_record, cluster))

        self.db.commit()

        # Sort by score descending
        opportunities.sort(key=lambda x: x[0].score, reverse=True)

        return [
            OpportunityResponse(
                id=opp.id,
                cluster_id=cluster.id,
                cluster_label=cluster.label,
                category=cluster.category,
                score=opp.score,
                counter_angle=opp.counter_angle,
                formats=json.loads(opp.formats_json) if opp.formats_json else [],
                headlines=json.loads(opp.headlines_json) if opp.headlines_json else [],
                primary_text=opp.primary_text,
                missing_proof=json.loads(opp.missing_proof_json) if opp.missing_proof_json else [],
                status=opp.status,
                created_at=opp.created_at,
            )
            for opp, cluster in opportunities
        ]

    def _build_counter_angle(self, category: str, profile: Optional[BusinessProfile]) -> str:
        name = profile.name if profile else "BrandMonk Academy"
        if category == "pricing_clarity":
            return f"Answer-first transparency: Disclose full batch syllabus and payment terms upfront so prospects choose {name} without hesitation."
        elif category == "placement_claims":
            return f"Proof-first angle: Showcase actual alumni portfolio links and verifiable project outcomes rather than abstract guarantees."
        elif category == "schedule_clarity":
            return f"Commitment angle: Announce confirmed weekend and evening batch timings with mentor review slots."
        return f"Direct counter-positioning highlighting {name}'s approved quality claims."

    def generate_draft(self, opportunity_id: int) -> OpportunityDraftResponse:
        opp = self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opp:
            raise ValueError(f"Opportunity {opportunity_id} not found.")

        cluster = opp.cluster
        profile = (
            self.db.query(BusinessProfile)
            .filter(BusinessProfile.is_active == True)
            .order_by(BusinessProfile.id.desc())
            .first()
        )

        approved_claims = [c.text for c in profile.claims if c.approved] if profile else []
        name = profile.name if profile else "BrandMonk Academy"

        headlines = [
            f"Doubts about {cluster.category.replace('_', ' ')}? Get the complete picture at {name}.",
            f"No hidden fees. No vague promises. Just verified training.",
            f"Join {name} — structured batches with mentor reviews every week.",
        ]

        # Enforce approved claims hard guardrail
        primary_body = (
            f"When choosing a training institute, uncertainty is costly. At {name}, every fact is public: "
            + (f" Approved: {'; '.join(approved_claims[:2])}." if approved_claims else " No hidden asterisks.")
            + " Book your free consultation to inspect our syllabus and past projects."
        )

        missing_claims = []
        if not approved_claims:
            missing_claims.append("No approved claims in profile. Add and approve claims to include specific factual proofs.")

        compliance_note = (
            "Advertising Compliance Reminder: All stated course durations, fees, and outcomes must strictly match "
            "approved claims and verifiable records. Avoid unsubstantiated employment guarantees."
        )

        return OpportunityDraftResponse(
            opportunity_id=opp.id,
            headline_options=headlines,
            primary_text=primary_body,
            cta=profile.preferred_cta if profile else "Book a free demo",
            recommended_format="Answer-First Static Poster or Carousel",
            used_claims=approved_claims[:3],
            missing_claims=missing_claims,
            compliance_note=compliance_note,
        )
