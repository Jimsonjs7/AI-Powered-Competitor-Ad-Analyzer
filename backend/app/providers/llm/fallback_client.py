from typing import List, Optional
from app.providers.llm.base import LLMClient
from app.schemas.analysis import AdAnalysisSchema, VisualStyle


class FallbackLLMClient(LLMClient):
    name = "deterministic_rubric_fallback"

    def analyze(
        self,
        *,
        images: List[str],
        copy_text: str,
        headline: Optional[str] = None,
        cta: Optional[str] = None,
        running_days: int = 1,
    ) -> AdAnalysisSchema:
        lower_copy = (copy_text + " " + (headline or "")).lower()

        # Rubric scoring calculation
        base_score = 65
        tactics = []
        emotional_triggers = []

        if any(w in lower_copy for w in ["days", "week", "month", "timeline", "batches"]):
            base_score += 8
            tactics.append("Fixed timeline")
            emotional_triggers.append("Time clarity")

        if any(w in lower_copy for w in ["hired", "placement", "job", "career", "salary"]):
            base_score += 10
            tactics.append("Placement promise")
            emotional_triggers.append("Career security")

        if any(w in lower_copy for w in ["free", "demo", "trial", "discount", "₹"]):
            base_score += 5
            tactics.append("Risk reversal")
            emotional_triggers.append("Financial ease")

        if any(w in lower_copy for w in ["portfolio", "project", "live", "hands-on"]):
            base_score += 6
            tactics.append("Practical proof")
            emotional_triggers.append("Competence confidence")

        if running_days > 45:
            base_score += 5

        effectiveness_score = min(95, max(50, base_score))

        # Infer subject course
        course = "AI"
        if "marketing" in lower_copy or "seo" in lower_copy or "ads" in lower_copy:
            course = "Digital marketing"
        elif "ui" in lower_copy or "ux" in lower_copy or "design" in lower_copy or "figma" in lower_copy:
            course = "UI/UX"

        return AdAnalysisSchema(
            course=course,
            hook=headline or "Direct outcome guarantee",
            offer="Free trial session with career mentor review",
            cta=cta or "Enroll now",
            target_audience="College graduates and early-career switchers looking for verified outcomes",
            emotional_triggers=emotional_triggers or ["Career aspiration", "Urgency"],
            persuasion_tactics=tactics or ["Practical proof", "Fixed timeline"],
            visual_style=VisualStyle(
                palette=["#12324F", "#F2B84B", "#FFFFFF"],
                layout="4:5 vertical card with high-contrast headline block",
                typography="Sans-serif bold headline with high legibility",
            ),
            why_it_works="Aligns clear career timeline with low friction entry point.",
            weaknesses="Lacks concrete student compensation proof or verified graduate reviews.",
            effectiveness_score=effectiveness_score,
            brandmonk_opportunity="Emphasize BrandMonk Academy's 1-on-1 mentor reviews, live studio projects, and verified alumni results in Coimbatore.",
        )
