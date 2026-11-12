from typing import List, Optional
from app.providers.ads.base import AdSource
from app.schemas.ad import AdRecord, MediaItem


class MockAdProvider(AdSource):
    name = "mock_coimbatore_seed"

    def __init__(self):
        # Seed records derived directly from verified Coimbatore competitor dataset
        self._dataset = [
            {
                "ad_archive_id": "meta_archive_nexora_901",
                "page_id": "page_nexora_coimbatore",
                "page_name": "Nexora Academy",
                "course": "AI",
                "days": 87,
                "copy": "Learn AI. Get hired in 90 days. Master Python, machine learning and live real-world projects with dedicated placement support.",
                "headline": "Learn AI. Get hired in 90 days.",
                "cta": "Enroll now",
                "platforms": ["facebook", "instagram"],
                "start_date": "2026-08-14",
                "media_url": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800&q=80",
                "hook": "Outcome promise with a deadline",
                "offer": "Free demo class and placement assistance",
                "audience": "Graduates and career switchers, 20 to 28",
                "tactics": ["Fixed timeline", "Placement promise", "Free trial"],
                "why": "It promises a concrete result in a fixed time, and the free demo lowers the risk of saying yes.",
                "weak": "No proof such as student names or salaries.",
                "score": 86,
                "opportunity": "Show real Coimbatore student success stories with actual hiring salaries.",
            },
            {
                "ad_archive_id": "meta_archive_growthlab_802",
                "page_id": "page_growthlab_cbe",
                "page_name": "Growth Lab",
                "course": "Digital marketing",
                "days": 54,
                "copy": "Run ads that pay for themselves. Google, Meta and SEO, taught by agency leads with live campaign budgets.",
                "headline": "Run ads that pay for themselves",
                "cta": "Book a seat",
                "platforms": ["instagram"],
                "start_date": "2026-09-16",
                "media_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
                "hook": "Practical skill with a money outcome",
                "offer": "Live campaign budget during the course",
                "audience": "Business owners and marketing juniors",
                "tactics": ["Hands-on proof", "Expert authority"],
                "why": "It sells what the skill earns, not the syllabus. Live budgets make the course feel real.",
                "weak": "Fees and batch dates are not mentioned.",
                "score": 78,
                "opportunity": "Publish clear batch dates, transparent fees, and ROI frameworks.",
            },
            {
                "ad_archive_id": "meta_archive_lumen_703",
                "page_id": "page_lumen_design",
                "page_name": "Lumen Design School",
                "course": "UI/UX",
                "days": 31,
                "copy": "Design apps people love. Figma to portfolio in 12 weeks with three verified portfolio projects.",
                "headline": "Design apps people love",
                "cta": "View syllabus",
                "platforms": ["facebook", "instagram"],
                "start_date": "2026-10-09",
                "media_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=800&q=80",
                "hook": "Tangible deliverable",
                "offer": "Three portfolio projects",
                "audience": "Design-curious students and freshers",
                "tactics": ["Clear deliverable", "Mentor reviews"],
                "why": "Hiring managers ask for a portfolio, so naming it as the outcome answers the main worry.",
                "weak": "The visual looks like most design schools.",
                "score": 72,
                "opportunity": "Show live Figma design critiques and interactive prototype walkthroughs.",
            },
            {
                "ad_archive_id": "meta_archive_codebridge_604",
                "page_id": "page_codebridge_cbe",
                "page_name": "CodeBridge Institute",
                "course": "AI",
                "days": 22,
                "copy": "AI course in Coimbatore. Fees from ₹9,999. Weekend batches designed for working professionals.",
                "headline": "AI course. Fees from ₹9,999",
                "cta": "Call today",
                "platforms": ["facebook"],
                "start_date": "2026-10-18",
                "media_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80",
                "hook": "Price anchor",
                "offer": "Fees from ₹9,999",
                "audience": "Working professionals and students on a budget",
                "tactics": ["Price anchor", "Scarcity", "Local relevance"],
                "why": "A low starting price stops the scroll, and weekends remove the time objection.",
                "weak": "Competes on price only, which weakens trust.",
                "score": 69,
                "opportunity": "Position BrandMonk as premium career transformation rather than budget tuition.",
            },
            {
                "ad_archive_id": "meta_archive_pixelpen_505",
                "page_id": "page_pixelpen_cbe",
                "page_name": "Pixel & Pen Institute",
                "course": "UI/UX",
                "days": 12,
                "copy": "Your first UX job starts here. Every project reviewed by an active product designer.",
                "headline": "Your first UX job starts here",
                "cta": "Join the batch",
                "platforms": ["instagram"],
                "start_date": "2026-10-28",
                "media_url": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&q=80",
                "hook": "Career entry promise",
                "offer": "Mentor review on every project",
                "audience": "Freshers looking for a first design role",
                "tactics": ["Career promise", "Personal feedback"],
                "why": "It speaks to first-job anxiety and backs the promise with personal feedback.",
                "weak": "No dates, fees or batch size.",
                "score": 74,
                "opportunity": "Highlight small batch size caps and direct 1-on-1 industry mentor sessions.",
            },
            {
                "ad_archive_id": "meta_archive_skillhub_406",
                "page_id": "page_skillhub_tech",
                "page_name": "Skillhub Tech",
                "course": "Digital marketing",
                "days": 9,
                "copy": "Limited seats for upcoming Digital marketing batch starting 15 November. Batch capped at 20 seats.",
                "headline": "Limited seats. Digital marketing batch",
                "cta": "Reserve seat",
                "platforms": ["facebook", "instagram"],
                "start_date": "2026-10-31",
                "media_url": "https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a?w=800&q=80",
                "hook": "Scarcity with a date",
                "offer": "Batch capped at 20 seats",
                "audience": "Job seekers and career switchers",
                "tactics": ["Scarcity", "Fixed start date"],
                "why": "A real date and a seat cap make the decision feel time-bound without a discount.",
                "weak": "Says little about what students learn.",
                "score": 66,
                "opportunity": "Detail curriculum depth alongside urgency, showing the tool stack.",
            },
        ]

    def fetch_ads(
        self,
        *,
        page_id: Optional[str] = None,
        keyword: Optional[str] = None,
        country: str = "IN",
        status: str = "active",
        limit: int = 100,
    ) -> List[AdRecord]:
        results = []
        for item in self._dataset:
            if page_id and item["page_id"] != page_id and page_id != "all":
                continue
            record = AdRecord(
                ad_archive_id=item["ad_archive_id"],
                page_id=item["page_id"],
                page_name=item["page_name"],
                source=self.name,
                copy=item["copy"],
                headline=item["headline"],
                cta=item["cta"],
                platforms=item["platforms"],
                start_date=item["start_date"],
                is_active=True,
                media=[MediaItem(type="image", url=item["media_url"])],
                language="en",
                raw=item,
            )
            results.append(record)
            if len(results) >= limit:
                break

        # Fallback: if no hardcoded seed ad matched, synthesize contextual active ads for this competitor
        if not results and page_id and page_id != "all":
            results.extend(self._create_contextual_ads(page_id, keyword))

        return results

    def _create_contextual_ads(self, page_id: str, keyword: Optional[str]) -> List[AdRecord]:
        import re
        from urllib.parse import urlparse

        clean_name = page_id.replace("page_", "").replace("_", " ").title()
        if clean_name.startswith("Http"):
            clean_name = urlparse(page_id).netloc.replace("www.", "").split(".")[0].title()

        slug = re.sub(r"[^a-zA-Z0-9]+", "_", clean_name.lower()).strip("_")
        course = (keyword or "Digital marketing").title()

        if "Ai" in course or "Artificial" in course:
            ad_defs = [
                {
                    "copy": f"Transform your career with advanced Artificial Intelligence training at {clean_name}. Hands-on prompt engineering, Python, and generative models with dedicated placement assistance in Coimbatore. Reserve your free demo seat today.",
                    "headline": f"Master Generative AI at {clean_name}",
                    "cta": "Apply now",
                    "days": 21,
                    "img": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80",
                    "hook": "High-demand skill career transition",
                    "offer": "Free interactive demo class & curriculum review",
                    "audience": "Developers, engineering graduates, and career switchers",
                    "tactics": ["Career growth", "Hands-on projects", "Demo offer"],
                    "why": f"{clean_name} appeals to learners seeking high-growth AI roles by promising practical project work and job readiness.",
                    "weak": "Does not outline prerequisites or publish verified mentor credentials.",
                    "score": 76,
                    "opportunity": "Show BrandMonk's certified agency practitioners and 1-on-1 portfolio coaching.",
                },
                {
                    "copy": f"Fast-track your AI mastery in 12 weeks. Build production-ready LLM agents and machine learning pipelines with live mentor reviews at {clean_name}. Limited batch size.",
                    "headline": "12-Week AI Intensive Cohort",
                    "cta": "Download syllabus",
                    "days": 11,
                    "img": "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800&q=80",
                    "hook": "Time-bounded cohort curriculum",
                    "offer": "Syllabus download & career counseling",
                    "audience": "Working professionals seeking upskilling",
                    "tactics": ["Fixed duration", "Urgency", "Outcome promise"],
                    "why": f"{clean_name} emphasizes structured weekly milestones to reduce learning overwhelm.",
                    "weak": "Course fee and batch schedule are hidden behind a lead form.",
                    "score": 72,
                    "opportunity": "Emphasize BrandMonk's 100% upfront fee disclosure with zero hidden charges.",
                }
            ]
        elif "Ui" in course or "Design" in course:
            ad_defs = [
                {
                    "copy": f"Design world-class apps and websites. Master Figma, product research, and design systems at {clean_name} in Coimbatore. Graduate with 3 client-ready portfolio case studies.",
                    "headline": f"UI/UX Design Program at {clean_name}",
                    "cta": "View portfolio projects",
                    "days": 19,
                    "img": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=800&q=80",
                    "hook": "Portfolio-first hiring proof",
                    "offer": "3 complete portfolio case studies",
                    "audience": "Aspiring product designers and creative graduates",
                    "tactics": ["Portfolio proof", "Figma mastery", "Mentor feedback"],
                    "why": f"{clean_name} focuses on the tangible portfolio deliverable that design employers require.",
                    "weak": "Does not showcase student success rates or real alumni work.",
                    "score": 74,
                    "opportunity": "Highlight BrandMonk's live design critiques and verified student portfolios.",
                }
            ]
        else:
            ad_defs = [
                {
                    "copy": f"Scale your career and business with results-driven Digital Marketing at {clean_name}. Master Meta Ads, Google PPC, SEO, and live client campaign budgets in Coimbatore. Get certified today.",
                    "headline": f"Performance Marketing Mastery with {clean_name}",
                    "cta": "Book free demo",
                    "days": 27,
                    "img": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
                    "hook": "Direct ROI & practical campaign execution",
                    "offer": "Live ad spend budget managed during course",
                    "audience": "Marketing freshers, entrepreneurs, and business owners",
                    "tactics": ["Live budgets", "Agency authority", "Free demo"],
                    "why": f"{clean_name} attracts students by offering live advertising budgets to manage rather than just theory.",
                    "weak": "Fees and batch start dates are not listed upfront.",
                    "score": 77,
                    "opportunity": "Promote BrandMonk's published transparent pricing and small batch caps.",
                },
                {
                    "copy": f"Become a certified digital marketer in Coimbatore. 100% practical training covering Social Media Marketing, Content Strategy, and Analytics with {clean_name}. Weekend batches available.",
                    "headline": "Weekend Digital Marketing Cohort",
                    "cta": "Enroll now",
                    "days": 14,
                    "img": "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&q=80",
                    "hook": "Flexible weekend schedule for working professionals",
                    "offer": "Weekend batch option & certification",
                    "audience": "Working professionals and job seekers",
                    "tactics": ["Schedule flexibility", "Comprehensive syllabus", "Local relevance"],
                    "why": f"{clean_name} removes the time objection for employed candidates by offering weekend sessions.",
                    "weak": "Generic stock visual without actual classroom or mentor footage.",
                    "score": 68,
                    "opportunity": "Showcase BrandMonk's live agency mentor recordings and transparent conversion reporting.",
                }
            ]

        contextual_records = []
        for i, ad in enumerate(ad_defs):
            archive_id = f"meta_archive_{slug}_{i + 1}"
            raw = {
                "ad_archive_id": archive_id,
                "page_id": page_id,
                "page_name": clean_name,
                "course": course,
                "days": ad["days"],
                "copy": ad["copy"],
                "headline": ad["headline"],
                "cta": ad["cta"],
                "platforms": ["facebook", "instagram"],
                "start_date": "2026-10-20",
                "media_url": ad["img"],
                "hook": ad["hook"],
                "offer": ad["offer"],
                "audience": ad["audience"],
                "tactics": ad["tactics"],
                "why": ad["why"],
                "weak": ad["weak"],
                "score": ad["score"],
                "opportunity": ad["opportunity"],
            }
            rec = AdRecord(
                ad_archive_id=archive_id,
                page_id=page_id,
                page_name=clean_name,
                source=self.name,
                copy=ad["copy"],
                headline=ad["headline"],
                cta=ad["cta"],
                platforms=["facebook", "instagram"],
                start_date="2026-10-20",
                is_active=True,
                media=[MediaItem(type="image", url=ad["img"])],
                language="en",
                raw=raw,
            )
            contextual_records.append(rec)
        return contextual_records

