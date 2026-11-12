from datetime import datetime, timezone
import json
import re
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import get_logger
from app.models.ad import Ad
from app.models.competitor import Competitor
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

        client_name = profile.name if profile and profile.name else "BrandMonk Academy"
        city = profile.city if profile and profile.city else "Coimbatore"
        preferred_cta = profile.preferred_cta if profile and profile.preferred_cta else "Book a free demo class"

        approved_claims = [c.text for c in profile.claims if c.approved] if profile else []
        if not approved_claims:
            approved_claims = [
                "100% upfront transparent course fee with zero hidden charges",
                "Live agency practitioner mentors with small batches capped at 15 students",
                "Hands-on training with real client projects and verified capstone portfolios",
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

    def _gather_live_market_context(self, course: str, city: str) -> Dict[str, Any]:
        """Aggregate real-time competitor hooks, longevity, and weaknesses from the live DB."""
        peer_ads = (
            self.db.query(Ad)
            .join(Competitor)
            .filter(Ad.is_active == True, Competitor.course == course)
            .order_by(Ad.run_days.desc())
            .limit(20)
            .all()
        )
        hooks = []
        weaknesses = []
        total_days = 0
        longest_headline = None
        for peer in peer_ads:
            total_days += peer.run_days or 1
            if not longest_headline and peer.headline:
                longest_headline = f"{peer.headline} ({peer.run_days}d active)"
            if peer.analysis:
                if peer.analysis.hook:
                    hooks.append(peer.analysis.hook)
                if peer.analysis.weaknesses:
                    weaknesses.append(peer.analysis.weaknesses)

        avg_days = round(total_days / len(peer_ads), 1) if peer_ads else 0
        return {
            "current_period": datetime.now(timezone.utc).strftime("%B %Y"),
            "city": city,
            "course": course,
            "active_competitor_ads": len(peer_ads),
            "avg_run_days": avg_days,
            "longest_running_ad": longest_headline or "N/A",
            "common_hooks": list(dict.fromkeys(hooks))[:5],
            "common_weaknesses": list(dict.fromkeys(weaknesses))[:5],
        }

    def _generate_angles_with_gemini(
        self,
        *,
        client_name: str,
        city: str,
        course: str,
        approved_claims: List[str],
        cta: str,
        audit: CompetitorAdFlawAudit,
        market_ctx: Dict[str, Any],
    ) -> Optional[List[CounterCreativeAngle]]:
        """Call Gemini to synthesize live, time-aware market trends & 3 counter-angles."""
        keys_pool = settings.all_gemini_api_keys
        if not keys_pool:
            return None

        prompt = f"""
You are a senior performance marketing strategist for {client_name}, a training institute in {city} teaching {course}.
Current Date: {market_ctx['current_period']}.

LIVE LOCAL MARKET SIGNALS ({city} - {course}):
- Active Competitor Ads Tracked: {market_ctx['active_competitor_ads']}
- Average Ad Longevity: {market_ctx['avg_run_days']} days
- Longest-Running Local Ad: {market_ctx['longest_running_ad']}
- Top Hooks Competitors Are Repeating: {json.dumps(market_ctx['common_hooks'])}
- Top Competitor Weaknesses: {json.dumps(market_ctx['common_weaknesses'])}

TARGET COMPETITOR AD TO COUNTER:
- Competitor: {audit.competitor_name}
- Headline: {audit.headline}
- Copy Snippet: {audit.copy_snippet}
- Vulnerabilities: {json.dumps(audit.vulnerabilities)}
- Unaddressed Student Doubts: {json.dumps(audit.unaddressed_prospect_doubts)}

STRICT GUARDRAIL - BRANDMONK APPROVED CLAIMS (USE ONLY THESE FACTS):
{json.dumps(approved_claims)}

TASK:
Based on TODAY'S ({market_ctx['current_period']}) real-world industry trend in {course} AND the live local competitor weaknesses above, generate EXACTLY 3 counter-ad angles as a JSON array of 3 objects.
The 3 objects MUST have these exact angle_type and angle_name pairs:
1. angle_type: "contrarian", angle_name: "Challenge the Cliché"
2. angle_type: "proof_roi", angle_name: "Real Results & Proof"
3. angle_type: "transparency", angle_name: "Upfront Fees & Honesty"

Each object must strictly match these JSON keys:
- angle_type (string)
- angle_name (string)
- strategic_rationale (string: explain the {market_ctx['current_period']} market trend + how this beats {audit.competitor_name})
- target_flaw_in_competitor (string)
- matching_approved_claim (string: exact quote from approved claims list)
- hook (string)
- headline (string, <8 words)
- subline (string)
- primary_text (string: student/learner-focused ad copy with bullet points, NOT agency/retainer copy)
- cta_text (string, use "{cta}")
- urgency_tagline (string)
- visual_concept (string)
- composition (string)
- color_palette (list of 4 hex strings, starting with "#0A7C6E")
- typography_guide (string)
- aspect_ratios (object with keys "1:1", "4:5", "9:16" containing clean image prompts with no text)
- image_prompt (string: clean photography prompt with no text/letters)
- negative_prompt (string)
"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json", "temperature": 0.4},
        }

        for idx, key in enumerate(keys_pool):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={key}"
            try:
                with httpx.Client(timeout=8.0) as client:
                    res = client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        parsed = json.loads(raw_text)
                        if isinstance(parsed, list) and len(parsed) == 3:
                            return [CounterCreativeAngle.model_validate(item) for item in parsed]
            except Exception as e:
                logger.warning(f"Gemini counter-angle call failed on key #{idx + 1}: {e}")

        return None

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
        market_ctx = self._gather_live_market_context(course, city)

        # Try live AI market-trend synthesis first
        ai_angles = self._generate_angles_with_gemini(
            client_name=client_name,
            city=city,
            course=course,
            approved_claims=approved_claims,
            cta=cta,
            audit=audit,
            market_ctx=market_ctx,
        )
        if ai_angles:
            return ai_angles

        claim_1 = approved_claims[0] if len(approved_claims) > 0 else "100% upfront transparent course fee with zero hidden charges"
        claim_2 = approved_claims[1] if len(approved_claims) > 1 else "Live agency practitioner mentors with small batches capped at 15 students"
        claim_3 = approved_claims[2] if len(approved_claims) > 2 else "Hands-on training with real client projects and verified capstone portfolios"

        # Current 2026 market trend & course-specific positioning
        course_l = course.lower()
        if "ai" in course_l or "artificial" in course_l:
            trend_shift = "Agentic AI workflows, RAG pipelines & deployed LLM apps (not static Python slides)"
            outdated_cliche = "outdated textbook ML theory and paper certificates"
            proof_metric = "deployed GitHub AI agents & live LLM portfolio projects"
            headline_1 = "Skip AI Slides. Build Live AI Agents."
            headline_2 = "Real AI Projects. Real Hiring Proof."
            headline_3 = "Upfront AI Course Fees. Zero Surprises."
        elif "ui" in course_l or "ux" in course_l or "design" in course_l:
            trend_shift = "AI-assisted Figma workflows, design systems & interactive user-tested prototypes"
            outdated_cliche = "copy-paste Dribbble templates and static wireframes"
            proof_metric = "3 audited product case studies reviewed by working UX leads"
            headline_1 = "Beyond Templates. Design Real Products."
            headline_2 = "Live Figma Critiques. Hireable Portfolios."
            headline_3 = "Clear Design Fees. Small 15-Seat Batches."
        else:
            trend_shift = "AI-powered Meta/Google Ads automation, GA4 attribution & live client ad budgets"
            outdated_cliche = "outdated SEO checklists and theoretical marketing slides"
            proof_metric = "live ROAS campaign dashboards & real client ad spend"
            headline_1 = "Don't Just Study Ads. Run Live Campaigns."
            headline_2 = "Real Ad Budgets. Verified ROAS Proof."
            headline_3 = "Upfront Course Fees. Zero Hidden Charges."

        angles = []

        # Angle 1: Challenge the Cliché
        angle_1 = CounterCreativeAngle(
            angle_type="contrarian",
            angle_name="Challenge the Cliché",
            strategic_rationale=(
                f"Counters {audit.competitor_name}'s '{audit.detected_hook}' by tapping into the 2026 {course} market shift toward {trend_shift}, "
                f"exposing why {outdated_cliche} no longer gets students hired."
            ),
            target_flaw_in_competitor=audit.vulnerabilities[0],
            matching_approved_claim=claim_1,
            hook=f"Still learning {outdated_cliche} in {city}? Here is what recruiters actually test in 2026.",
            headline=headline_1,
            subline=f"{client_name} · {trend_shift}",
            primary_text=(
                f"Most {course} courses in {city} still teach {outdated_cliche} while the industry has moved to {trend_shift}.\n\n"
                f"At {client_name}, you learn by building real work:\n"
                f"• {claim_1}\n"
                f"• {proof_metric.capitalize()}\n"
                f"• Direct mentorship from active industry practitioners\n\n"
                f"See our live curriculum and student work before you enroll."
            ),
            cta_text=cta,
            urgency_tagline="Next cohort capped at 15 students",
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
                "1:1": f"Social media ad poster, square 1080x1080 format, modern {course} training studio in {city}, clean teal #0A7C6E accents, minimal aesthetic, negative space top-left for text overlay, no lettering in image.",
                "4:5": f"Social media ad creative, portrait 1080x1350 format, modern desk with laptop showing {course} workflow, teal #0A7C6E accents, ample negative space at top, no lettering.",
                "9:16": f"Vertical story ad creative, 1080x1920 format, sleek minimalist workspace with high contrast, teal #0A7C6E accent lighting, top half empty for bold text overlay, no lettering.",
            },
            image_prompt=(
                f"Editorial commercial photograph of a clean, minimalist training studio workspace in {city}, "
                f"sleek laptop on desk showing modern {course} workflow, subtle deep teal (#0A7C6E) lighting, "
                f"modern architecture, crisp 8k resolution, leave top half completely clean for headline overlay, draw no lettering or text."
            ),
            negative_prompt="text, letters, words, watermark, logo, messy, blurry, cartoon, low quality",
        )
        angles.append(angle_1)

        # Angle 2: Real Results & Proof
        angle_2 = CounterCreativeAngle(
            angle_type="proof_roi",
            angle_name="Real Results & Proof",
            strategic_rationale=(
                f"Outperforms {audit.competitor_name}'s lack of verifiable outcomes by leading with {proof_metric}, "
                f"directly answering student doubts about real-world job readiness."
            ),
            target_flaw_in_competitor=audit.vulnerabilities[1] if len(audit.vulnerabilities) > 1 else audit.vulnerabilities[0],
            matching_approved_claim=claim_2,
            hook=f"Before paying for a {course} certificate, ask to see actual student {proof_metric}.",
            headline=headline_2,
            subline=f"{client_name} · {claim_2}",
            primary_text=(
                f"Hiring managers in 2026 don't hire paper certificates — they hire {proof_metric}.\n\n"
                f"How {client_name} prepares learners in {city}:\n"
                f"• {claim_2}\n"
                f"• Training aligned with {trend_shift}\n"
                f"• 1-on-1 portfolio reviews every week\n\n"
                f"Join a free live demo session and review real student projects."
            ),
            cta_text=cta,
            urgency_tagline="Review live student portfolios",
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
                "1:1": f"Modern {course} training creative, 1:1 square, macro view of sleek student portfolio work, deep teal #0A7C6E branding, clean negative space at top for overlay, no text.",
                "4:5": f"Portrait ed-tech ad creative, 4:5 format, mentor reviewing live {course} project with student on monitor, soft studio lighting, teal #0A7C6E, top 40% empty space for copy, no text.",
                "9:16": f"Vertical story ad, 9:16 aspect ratio, sleek mobile screen showing clean verified project showcase, modern minimalist aesthetic, upper third empty for text, no lettering.",
            },
            image_prompt=(
                f"Premium commercial photograph, experienced mentor guiding a student at a modern desk in {city}, "
                f"subtle screen showing {course} project work, tasteful deep teal #0A7C6E and white aesthetic, "
                f"cinematic natural lighting, upper third has clean space for headline, draw no lettering or text."
            ),
            negative_prompt="text, lettering, watermark, messy, fake stock photo look, blurry, distorted",
        )
        angles.append(angle_2)

        # Angle 3: Upfront Fees & Honesty
        angle_3 = CounterCreativeAngle(
            angle_type="transparency",
            angle_name="Upfront Fees & Honesty",
            strategic_rationale=(
                f"Directly exploits {audit.competitor_name}'s pricing and batch ambiguity by giving students upfront fee clarity, "
                f"building immediate trust without pushy sales calls."
            ),
            target_flaw_in_competitor=audit.unaddressed_prospect_doubts[0] if audit.unaddressed_prospect_doubts else "Hidden pricing ambiguity",
            matching_approved_claim=claim_3,
            hook=f"Tired of 'DM for fees' and surprise exam or certification charges?",
            headline=headline_3,
            subline=f"{client_name} · {claim_3}",
            primary_text=(
                f"Choosing a {course} institute in {city} shouldn't require sitting through high-pressure sales calls just to learn the fee.\n\n"
                f"Our promise at {client_name}:\n"
                f"• {claim_3}\n"
                f"• Small batches capped at 15 students for personal attention\n"
                f"• Full syllabus & batch schedule shared upfront\n\n"
                f"Book a no-pressure demo class and see the full roadmap."
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

