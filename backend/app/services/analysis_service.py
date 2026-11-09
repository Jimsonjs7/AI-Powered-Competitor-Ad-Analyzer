import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from app.models.ad import Ad
from app.models.analysis import AdAnalysis
from app.providers.llm.base import LLMClient
from app.providers.llm.gemini_client import GeminiLLMClient
from app.schemas.analysis import AdAnalysisSchema


class AnalysisService:
    def __init__(self, db: Session, llm_client: Optional[LLMClient] = None):
        self.db = db
        self.llm = llm_client or GeminiLLMClient()

    def analyze_ad(self, ad_id: int) -> AdAnalysisSchema:
        ad = self.db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            raise ValueError(f"Ad with id {ad_id} not found")

        content_blob = f"{ad.copy}|{ad.headline or ''}|{ad.cta or ''}"
        content_hash = hashlib.sha256(content_blob.encode()).hexdigest()

        # Check existing cached analysis
        if ad.analysis and ad.analysis.content_hash == content_hash:
            return self._to_schema(ad.analysis, ad.competitor.course if ad.competitor else "AI")

        # Call multimodal LLM
        schema_result = self.llm.analyze(
            images=[m.original_url for m in ad.media] if ad.media else [],
            copy_text=ad.copy,
            headline=ad.headline,
            cta=ad.cta,
            running_days=ad.run_days,
        )

        # Upsert analysis cache record
        if ad.analysis:
            analysis_obj = ad.analysis
        else:
            analysis_obj = AdAnalysis(ad_id=ad.id)
            self.db.add(analysis_obj)

        analysis_obj.effectiveness_score = schema_result.effectiveness_score
        analysis_obj.hook = schema_result.hook
        analysis_obj.offer = schema_result.offer
        analysis_obj.target_audience = schema_result.target_audience
        analysis_obj.tactics_str = ",".join(schema_result.persuasion_tactics)
        analysis_obj.emotional_triggers_str = ",".join(schema_result.emotional_triggers)
        analysis_obj.why_it_works = schema_result.why_it_works
        analysis_obj.weaknesses = schema_result.weaknesses
        analysis_obj.brandmonk_opportunity = schema_result.brandmonk_opportunity
        analysis_obj.content_hash = content_hash
        analysis_obj.model_name = self.llm.name

        self.db.commit()
        return schema_result

    def _to_schema(self, analysis: AdAnalysis, course: str) -> AdAnalysisSchema:
        return AdAnalysisSchema(
            course=course,
            hook=analysis.hook,
            offer=analysis.offer,
            cta="Enroll now",
            target_audience=analysis.target_audience,
            emotional_triggers=[t.strip() for t in analysis.emotional_triggers_str.split(",") if t.strip()],
            persuasion_tactics=[t.strip() for t in analysis.tactics_str.split(",") if t.strip()],
            why_it_works=analysis.why_it_works,
            weaknesses=analysis.weaknesses,
            effectiveness_score=analysis.effectiveness_score,
            brandmonk_opportunity=analysis.brandmonk_opportunity,
        )

