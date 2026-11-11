from datetime import datetime, timezone
import json
import re
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import get_logger
from app.models.ad import Ad
from app.models.profile import BusinessProfile
from app.schemas.creative_recommender import (
    CompetitorAdFlawAudit,
    CounterCreativeAngle,
    CreativeCounterAdResponse,
)

logger = get_logger("service.creative_recommender")


class CreativeRecommenderService:
    def __init__(self, db: Session):
        self.db = db

    def generate_recommendations(self, ad_id: int) -> CreativeCounterAdResponse:
        ad = self.db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            raise ValueError(f"Ad with ID {ad_id} not found.")

        # Get active business profile
        profile = (
            self.db.query(BusinessProfile)
            .filter(BusinessProfile.is_active == True)
            .order_by(BusinessProfile.id.desc())
            .first()
        )

        client_name = profile.name if profile and profile.name else "Brand Monk Consulting"
        city = profile.city if profile and profile.city else "Coimbatore"
        preferred_cta = profile.preferred_cta if profile and profile.preferred_cta else "Book a free consultation"

        approved_claims = [c.text for c in profile.claims if c.approved] if profile else []
        if not approved_claims:
            approved_claims = [
                "Customized performance marketing with transparent conversion reporting",
                "Dedicated growth managers with direct weekly communication",
                "Upfront transparent pricing with zero hidden software or onboarding charges",
            ]

        # 1. Competitor Ad Flaw Audit
        audit = self._audit_competitor_ad(ad)

        # 2. Generate 3 Strategic Counter Angles
        angles = self._build_counter_angles(ad, client_name, city, approved_claims, preferred_cta, audit)

        course_name = ad.competitor.course if ad.competitor else "Digital marketing"

        return CreativeCounterAdResponse(
            ad_id=ad.id,
            client_name=client_name,
            course=course_name,
            competitor_audit=audit,
            angles=angles,
            recommended_cta=preferred_cta,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

    def _audit_competitor_ad(self, ad: Ad) -> CompetitorAdFlawAudit:
        copy_text = ad.copy or ""
        headline_text = ad.headline or ""
        run_days = ad.run_days or 1
        comp_name = ad.competitor.name if ad.competitor else "Competitor"

        vulnerabilities = []
        unaddressed_doubts = []

        # Check for pricing mention
        has_price = bool(
            re.search(
                r"(?:[\$₹]|(?:rs\.?|inr|fees?|pricing|price)\b\s*\d+|\b\d+\s*(?:rs|inr|rupees|per\s+month|\/-\b))",
                copy_text,
                re.IGNORECASE,
            )
        )
        if not has_price:
            vulnerabilities.append("No pricing transparency in ad copy; creates doubt and lead friction.")
            unaddressed_doubts.append("Are there hidden setup fees or surprise retainer charges?")
        else:
            vulnerabilities.append("Competitor is competing on low-cost price discounting rather than ROI quality.")
            unaddressed_doubts.append("Is this service low quality because it is so cheap?")

        # Check for specific metrics/proof
        has_metrics = bool(re.search(r"(\b\d+%\b|\b\d+x\b|\b\d+\s*(lakh|k|cr)\b)", copy_text, re.IGNORECASE))
        if not has_metrics:
            vulnerabilities.append("Vague outcome claim with no concrete ROI figures or verifiable case studies.")
            unaddressed_doubts.append("What actual results will my business see in the first 30 days?")
        else:
            vulnerabilities.append("Uses generic metric claims without showing live client dashboards or proof of work.")
            unaddressed_doubts.append("Can they actually reproduce these results for my specific business niche?")

        # Fatigue level
        if run_days > 45:
            fatigue_level = "High Creative Fatigue (Running 45+ days)"
            vulnerabilities.append("Creative is oversaturated in the local feed; audience requires a strong visual pattern interrupt.")
        elif run_days > 14:
            fatigue_level = "Active Runner (14-45 days)"
            vulnerabilities.append("Established ad campaign; vulnerable to direct comparison and value contrast.")
        else:
            fatigue_level = "Fresh Creative (<14 days)"
            vulnerabilities.append("Early testing phase; vulnerable to aggressive counter-positioning on trust.")

        unaddressed_doubts.append("Will I get direct senior support or be handed off to an inexperienced junior?")

        detected_hook = ad.analysis.hook if ad.analysis and ad.analysis.hook else (
            "Discount-led offer" if has_price else "Generic outcome promise"
        )
        detected_offer = ad.analysis.offer if ad.analysis and ad.analysis.offer else (
            ad.headline or "General services"
        )

        return CompetitorAdFlawAudit(
            competitor_name=comp_name,
            headline=headline_text,
            copy_snippet=copy_text[:140] + ("..." if len(copy_text) > 140 else ""),
            active_days=run_days,
            detected_hook=detected_hook,
            detected_offer=detected_offer,
            vulnerabilities=vulnerabilities,
            creative_fatigue_level=fatigue_level,
            unaddressed_prospect_doubts=unaddressed_doubts,
        )

    def _build_counter_angles(
        self,
        ad: Ad,
        client_name: str,
        city: str,
        approved_claims: List[str],
        cta: str,
        audit: CompetitorAdFlawAudit,
    ) -> List[CounterCreativeAngle]:
        course = (ad.competitor.course if ad.competitor else None) or "Digital marketing"
        claim_1 = approved_claims[0] if len(approved_claims) > 0 else "Custom performance marketing with transparent conversion reporting"
        claim_2 = approved_claims[1] if len(approved_claims) > 1 else "Dedicated growth managers with direct weekly communication"
        claim_3 = approved_claims[2] if len(approved_claims) > 2 else "Upfront transparent pricing with zero hidden charges"

        angles = []

        # Angle 1: The Contrarian Pattern Interrupt
        angle_1 = CounterCreativeAngle(
            angle_type="contrarian",
            angle_name="The Contrarian Pattern Interrupt",
            strategic_rationale=(
                f"Shatters {audit.competitor_name}'s '{audit.detected_hook}' premise by directly addressing the hidden frustration "
                f"prospects face with generic agencies/institutes, positioning {client_name} as the mature alternative."
            ),
            target_flaw_in_competitor=audit.vulnerabilities[0],
            matching_approved_claim=claim_1,
            hook=f"Why 85% of businesses in {city} burn budget with generic {course.lower()} promises.",
            headline="Stop burning ad spend. Demand verified ROI.",
            subline=f"{client_name} · Transparent performance & weekly accountability",
            primary_text=(
                f"Tired of agencies promising the moon and delivering zero conversion clarity? "
                f"At {client_name}, we believe marketing should be measurable down to the rupee.\n\n"
                f"• {claim_1}\n"
                f"• Direct 1-on-1 strategy with senior specialists\n"
                f"• Zero lock-in retainers or surprise charges\n\n"
                f"Get the exact roadmap for your business before spending another rupee."
            ),
            cta_text=cta,
            urgency_tagline="Limited to 5 free audits this week",
            visual_concept=(
                "High-contrast split visual: left side features clean empty space with bold typography, "
                "right side shows a modern sleek laptop display with sharp ascending conversion graphs."
            ),
            composition=(
                "Hero element placed in the right third; ample negative space in top-left for high-contrast headline overlay. "
                "Accent color highlight on key metric points."
            ),
            color_palette=["#0A7C6E", "#111827", "#F6F7F5", "#FFFFFF"],
            typography_guide="Primary headline in 800 weight grotesque sans-serif; subline in 500 weight medium contrast.",
            aspect_ratios={
                "1:1": f"Social media ad poster, square 1080x1080 format, professional marketing workspace in {city}, clean teal #0A7C6E accents, minimal aesthetic, negative space top-left for text overlay, no lettering in image.",
                "4:5": f"Social media ad creative, portrait 1080x1350 format, modern executive desk with tablet showing clean analytics graphs, teal #0A7C6E accents, ample negative space at top, no lettering.",
                "9:16": f"Vertical story ad creative, 1080x1920 format, sleek minimalist business dashboard with high contrast, teal #0A7C6E accent lighting, top half empty for bold text overlay, no lettering.",
            },
            image_prompt=(
                f"Editorial commercial photograph of a clean, minimalist executive workspace in {city}, "
                f"sleek tablet on desk showing green conversion growth graph, subtle deep teal (#0A7C6E) lighting, "
                f"modern architecture, crisp 8k resolution, leave top half completely clean for headline overlay, draw no lettering or text."
            ),
            negative_prompt="text, letters, words, watermark, logo, messy, blurry, cartoon, low quality",
        )
        angles.append(angle_1)

        # Angle 2: Concrete Proof & Live ROI Contrast
        angle_2 = CounterCreativeAngle(
            angle_type="proof_roi",
            angle_name="Verified Proof & Live ROI Contrast",
            strategic_rationale=(
                f"Outperforms {audit.competitor_name}'s lack of evidence by leading with concrete client deliverables, "
                f"answering prospect doubts about whether results are reproducible."
            ),
            target_flaw_in_competitor=audit.vulnerabilities[1] if len(audit.vulnerabilities) > 1 else audit.vulnerabilities[0],
            matching_approved_claim=claim_2,
            hook=f"Before you commit to another {course.lower()} contract, ask to see their live dashboard.",
            headline="Real clients. Real revenue. No guesswork.",
            subline=f"{client_name} · {claim_2}",
            primary_text=(
                f"Anyone can make big claims on Meta ads. But can they show you live client results?\n\n"
                f"Here is how {client_name} delivers for clients across {city}:\n"
                f"• {claim_2}\n"
                f"• Clear conversion tracking set up from day 1\n"
                f"• Transparent cost-per-lead and return on ad spend\n\n"
                f"See our live case studies and client campaign breakdown today."
            ),
            cta_text=cta,
            urgency_tagline="View live client case studies",
            visual_concept=(
                "Macro focus on a high-precision analytics dashboard card displaying green conversion indicators, "
                "with an authentic professional strategist reviewing live performance in the background."
            ),
            composition=(
                "Focal point centered at bottom-right with soft depth-of-field background. "
                "Top 40% reserved strictly for high-contrast headline and bullet overlay."
            ),
            color_palette=["#0A7C6E", "#1E3A8A", "#F3F4F6", "#FFFFFF"],
            typography_guide="Headline in bold geometric sans; high contrast against neutral canvas background.",
            aspect_ratios={
                "1:1": f"Modern business growth creative, 1:1 square, macro view of sleek digital performance metrics card, deep teal #0A7C6E branding, clean negative space at top for overlay, no text.",
                "4:5": f"Portrait business ad creative, 4:5 format, confident professional reviewing clean growth analytics on monitor, soft studio lighting, teal #0A7C6E, top 40% empty space for copy, no text.",
                "9:16": f"Vertical story ad, 9:16 aspect ratio, sleek mobile screen showing clean verified performance reports, modern minimalist aesthetic, upper third empty for text, no lettering.",
            },
            image_prompt=(
                f"Premium commercial photograph, confident professional strategist at a modern desk in {city}, "
                f"subtle screen reflection showing clean green upward analytics chart, tasteful deep teal #0A7C6E and white aesthetic, "
                f"cinematic natural lighting, high end studio photography, upper third has clean space for headline, draw no lettering or text."
            ),
            negative_prompt="text, lettering, watermark, messy, fake stock photo look, blurry, distorted",
        )
        angles.append(angle_2)

        # Angle 3: Friction-Free Transparency & Zero Hidden Costs
        angle_3 = CounterCreativeAngle(
            angle_type="transparency",
            angle_name="Friction-Free Transparency & Zero Hidden Fees",
            strategic_rationale=(
                f"Directly exploits {audit.competitor_name}'s pricing ambiguity by presenting upfront transparency, "
                f"building trust with cost-conscious prospects who dislike surprise costs."
            ),
            target_flaw_in_competitor=audit.unaddressed_prospect_doubts[0] if audit.unaddressed_prospect_doubts else "Hidden pricing ambiguity",
            matching_approved_claim=claim_3,
            hook=f"Tired of surprise onboarding fees and ambiguous agency retainers?",
            headline="Upfront pricing. Zero surprise charges.",
            subline=f"{client_name} · {claim_3}",
            primary_text=(
                f"Most businesses in {city} have had at least one bad agency experience with hidden software add-ons and delayed replies.\n\n"
                f"We do things differently:\n"
                f"• {claim_3}\n"
                f"• Weekly milestone check-ins with senior mentors\n"
                f"• 100% ownership of all your ad accounts and creative assets\n\n"
                f"Talk to our team and get an upfront scope with zero commitment."
            ),
            cta_text=cta,
            urgency_tagline="Transparent pricing & zero lock-in",
            visual_concept=(
                "Ultra-clean Swiss minimalist design aesthetic: pure white/light grey canvas, bold geometric balance, "
                "single striking teal hero element symbolizing clarity and precision."
            ),
            composition=(
                "Minimalist balanced layout with clear grid lines, crisp negative space, and dedicated button container area."
            ),
            color_palette=["#0A7C6E", "#111827", "#E5E7EB", "#FFFFFF"],
            typography_guide="High contrast bold black headline with emerald teal highlight accents.",
            aspect_ratios={
                "1:1": f"Swiss minimalist ad poster, 1080x1080 square, clean white and teal aesthetic, architectural precision, open breathing space for headline overlay, no text.",
                "4:5": f"Minimalist social feed ad, 1080x1350 format, modern architectural lines, subtle teal #0A7C6E glass reflections, spacious negative space at top, no lettering.",
                "9:16": f"Vertical story creative, 1080x1920 format, high-end minimalist design with subtle teal glass gradient and ample safe space for typography overlay, no text.",
            },
            image_prompt=(
                f"High-end Swiss minimalist design photography, abstract architectural glass and light surface, "
                f"crisp clean geometric lines, accents of brand teal #0A7C6E on pure white and platinum grey, "
                f"exceptional studio lighting, 8k resolution, leave wide negative space for text overlay, draw no letters or text."
            ),
            negative_prompt="text, words, lettering, messy, cluttered, dark, gloomy, watermark",
        )
        angles.append(angle_3)

        return angles

