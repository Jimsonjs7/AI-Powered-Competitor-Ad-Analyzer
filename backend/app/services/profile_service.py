import json
import re
from datetime import datetime, timezone
from typing import Optional
import httpx
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.core.security import validate_target_url
from app.models.profile import BusinessProfile, ProfileClaim, ProfileService as ProfileServiceModel, ProfileSocialAccount
from app.schemas.profile import (
    AutofillResponse,
    AutofillSuggestion,
    BusinessProfileCreate,
    BusinessProfileResponse,
    BusinessProfileUpdate,
    CompletenessHint,
    ProfileClaimResponse,
    ProfileCompletenessResponse,
    ProfileServiceResponse,
    ProfileSocialAccountResponse,
)

logger = get_logger("service.profile")


class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    def get_active_profile(self) -> Optional[BusinessProfile]:
        return (
            self.db.query(BusinessProfile)
            .filter(BusinessProfile.is_active == True)
            .order_by(BusinessProfile.id.desc())
            .first()
        )

    def to_response(self, profile: BusinessProfile) -> BusinessProfileResponse:
        try:
            b_type = json.loads(profile.business_type_json) if profile.business_type_json else []
        except Exception:
            b_type = []

        try:
            domains = json.loads(profile.domains_json) if profile.domains_json else []
        except Exception:
            domains = []

        try:
            languages = json.loads(profile.languages_json) if profile.languages_json else ["English"]
        except Exception:
            languages = ["English"]

        try:
            thresholds = json.loads(profile.thresholds_json) if profile.thresholds_json else {"min_ads": 3, "min_reviews": 20, "min_comments": 15}
        except Exception:
            thresholds = {"min_ads": 3, "min_reviews": 20, "min_comments": 15}

        services = [
            ProfileServiceResponse(
                id=s.id,
                profile_id=s.profile_id,
                name=s.name,
                description=s.description,
                fee_min=s.fee_min,
                fee_max=s.fee_max,
                duration=s.duration,
                mode=s.mode,
                next_batch=s.next_batch,
                outcomes=s.outcomes,
            )
            for s in profile.services
        ]

        claims = [
            ProfileClaimResponse(
                id=c.id,
                profile_id=c.profile_id,
                text=c.text,
                proof_link=c.proof_link,
                approved=c.approved,
                created_at=c.created_at,
            )
            for c in profile.claims
        ]

        social = [
            ProfileSocialAccountResponse(
                id=a.id,
                profile_id=a.profile_id,
                platform=a.platform,
                url_or_handle=a.url_or_handle,
                verified=a.verified,
            )
            for a in profile.social_accounts
        ]

        return BusinessProfileResponse(
            id=profile.id,
            version=profile.version,
            name=profile.name,
            description=profile.description,
            tagline=profile.tagline,
            business_type=b_type,
            domains=domains,
            city=profile.city,
            area=profile.area,
            lat=profile.lat,
            lng=profile.lng,
            radius_km=profile.radius_km,
            website=profile.website,
            tone=profile.tone,
            target_audience=profile.target_audience,
            price_positioning=profile.price_positioning,
            languages=languages,
            primary_goal=profile.primary_goal,
            monthly_budget_range=profile.monthly_budget_range,
            preferred_cta=profile.preferred_cta,
            thresholds=thresholds,
            is_active=profile.is_active,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            services=services,
            claims=claims,
            social_accounts=social,
        )

    def upsert_profile(self, data: BusinessProfileCreate | BusinessProfileUpdate) -> BusinessProfileResponse:
        existing = self.get_active_profile()
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if existing:
            profile = existing
            profile.version += 1
            profile.updated_at = now
            if data.name is not None:
                profile.name = data.name
            if data.description is not None:
                profile.description = data.description
            if data.tagline is not None:
                profile.tagline = data.tagline
            if data.business_type is not None:
                profile.business_type_json = json.dumps(data.business_type)
            if data.domains is not None:
                profile.domains_json = json.dumps(data.domains)
            if data.city is not None:
                profile.city = data.city
            if data.area is not None:
                profile.area = data.area
            if data.lat is not None:
                profile.lat = data.lat
            if data.lng is not None:
                profile.lng = data.lng
            if data.radius_km is not None:
                profile.radius_km = data.radius_km
            if data.website is not None:
                profile.website = data.website
            if data.tone is not None:
                profile.tone = data.tone
            if data.target_audience is not None:
                profile.target_audience = data.target_audience
            if data.price_positioning is not None:
                profile.price_positioning = data.price_positioning
            if data.languages is not None:
                profile.languages_json = json.dumps(data.languages)
            if data.primary_goal is not None:
                profile.primary_goal = data.primary_goal
            if data.monthly_budget_range is not None:
                profile.monthly_budget_range = data.monthly_budget_range
            if data.preferred_cta is not None:
                profile.preferred_cta = data.preferred_cta
            if data.thresholds is not None:
                profile.thresholds_json = json.dumps(data.thresholds)

            # Update services if provided
            if data.services is not None:
                profile.services.clear()
                for s in data.services:
                    profile.services.append(
                        ProfileServiceModel(
                            name=s.name,
                            description=s.description,
                            fee_min=s.fee_min,
                            fee_max=s.fee_max,
                            duration=s.duration,
                            mode=s.mode,
                            next_batch=s.next_batch,
                            outcomes=s.outcomes,
                        )
                    )

            # Update claims if provided
            if data.claims is not None:
                profile.claims.clear()
                for c in data.claims:
                    profile.claims.append(
                        ProfileClaim(
                            text=c.text,
                            proof_link=c.proof_link,
                            approved=c.approved,
                        )
                    )

            # Update social accounts if provided
            if data.social_accounts is not None:
                profile.social_accounts.clear()
                for a in data.social_accounts:
                    profile.social_accounts.append(
                        ProfileSocialAccount(
                            platform=a.platform,
                            url_or_handle=a.url_or_handle,
                            verified=a.verified,
                        )
                    )
        else:
            profile = BusinessProfile(
                name=data.name or "BrandMonk Academy",
                description=data.description,
                tagline=data.tagline,
                business_type_json=json.dumps(data.business_type or ["training academy"]),
                domains_json=json.dumps(data.domains or ["AI", "Digital marketing", "UI/UX"]),
                city=data.city or "Coimbatore",
                area=data.area,
                lat=data.lat,
                lng=data.lng,
                radius_km=data.radius_km or 10.0,
                website=data.website,
                tone=data.tone or "Professional and outcome-focused",
                target_audience=data.target_audience,
                price_positioning=data.price_positioning or "mid",
                languages_json=json.dumps(data.languages or ["English"]),
                primary_goal=data.primary_goal or "enquiries",
                monthly_budget_range=data.monthly_budget_range,
                preferred_cta=data.preferred_cta or "Book a free demo",
                thresholds_json=json.dumps(data.thresholds or {"min_ads": 3, "min_reviews": 20, "min_comments": 15}),
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            self.db.add(profile)
            self.db.flush()

            if data.services:
                for s in data.services:
                    profile.services.append(
                        ProfileServiceModel(
                            name=s.name,
                            description=s.description,
                            fee_min=s.fee_min,
                            fee_max=s.fee_max,
                            duration=s.duration,
                            mode=s.mode,
                            next_batch=s.next_batch,
                            outcomes=s.outcomes,
                        )
                    )

            if data.claims:
                for c in data.claims:
                    profile.claims.append(
                        ProfileClaim(
                            text=c.text,
                            proof_link=c.proof_link,
                            approved=c.approved,
                        )
                    )

            if data.social_accounts:
                for a in data.social_accounts:
                    profile.social_accounts.append(
                        ProfileSocialAccount(
                            platform=a.platform,
                            url_or_handle=a.url_or_handle,
                            verified=a.verified,
                        )
                    )

        self.db.commit()
        self.db.refresh(profile)
        return self.to_response(profile)

    def get_completeness(self) -> ProfileCompletenessResponse:
        profile = self.get_active_profile()
        if not profile:
            return ProfileCompletenessResponse(
                score=0,
                missing_fields=[
                    CompletenessHint(
                        field="name",
                        hint="Set up your business name to initialize the profile.",
                        impact="Required",
                    ),
                    CompletenessHint(
                        field="city",
                        hint="Set up your business city to find local competitors.",
                        impact="Required",
                    ),
                    CompletenessHint(
                        field="domains",
                        hint="Specify your domains (e.g. AI, Digital marketing) for discovery matching.",
                        impact="Required",
                    ),
                ],
                is_ready_for_discovery=False,
            )

        score = 0
        hints = []

        # Required fields (30 points total)
        if profile.name:
            score += 15
        else:
            hints.append(CompletenessHint(field="name", hint="Business name is missing.", impact="High"))

        if profile.city:
            score += 15
        else:
            hints.append(CompletenessHint(field="city", hint="City location is missing.", impact="High"))

        # Offers & Services (20 points)
        if profile.services and len(profile.services) > 0:
            score += 20
        else:
            hints.append(
                CompletenessHint(
                    field="services",
                    hint="Add at least one course or service so the AI can draft price-led and outcome-led counter ads.",
                    impact="Medium",
                )
            )

        # Approved claims (20 points)
        approved_claims = [c for c in profile.claims if c.approved]
        if len(approved_claims) > 0:
            score += 20
        else:
            hints.append(
                CompletenessHint(
                    field="claims",
                    hint="Add approved claims. The AI is only allowed to use approved facts in counter-ad drafts.",
                    impact="High",
                )
            )

        # Website & Online Presence (15 points)
        if profile.website:
            score += 10
        else:
            hints.append(
                CompletenessHint(
                    field="website",
                    hint="Add website URL for automatic verification and competitor exclusion.",
                    impact="Low",
                )
            )

        if profile.social_accounts and len(profile.social_accounts) > 0:
            score += 5
        else:
            hints.append(
                CompletenessHint(
                    field="social_accounts",
                    hint="Add your public Facebook/Instagram page link to avoid competitor self-matching.",
                    impact="Low",
                )
            )

        # Positioning & Goals (15 points)
        if profile.target_audience:
            score += 5
        if profile.primary_goal:
            score += 5
        if profile.preferred_cta:
            score += 5

        is_ready = bool(profile.name and profile.city and score >= 50)
        return ProfileCompletenessResponse(
            score=min(100, score),
            missing_fields=hints,
            is_ready_for_discovery=is_ready,
        )

    def autofill_from_website(self, website_url: str) -> AutofillResponse:
        safe_url = validate_target_url(website_url, check_whitelist=False)
        title = None
        description = None
        suggestions = []

        def check_redirect_url(response: httpx.Response):
            redirect_loc = response.headers.get("Location")
            if redirect_loc:
                from urllib.parse import urljoin
                resolved_redirect = urljoin(str(response.url), redirect_loc)
                validate_target_url(resolved_redirect, check_whitelist=False)

        try:
            with httpx.Client(
                timeout=10.0,
                follow_redirects=True,
                event_hooks={"response": [check_redirect_url]},
            ) as client:
                res = client.get(safe_url, headers={"User-Agent": "BrandMonk-AdDesk/2.0"})
                if res.status_code == 200:
                    html = res.text
                    # Extract title
                    title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
                    if title_match:
                        title = title_match.group(1).strip()
                        parts = [p.strip() for p in re.split(r"[-|–—:]", title) if p.strip()]
                        seo_indicators = ["best ", "top ", " agency in", " company in", " services in", " institute in", " training in"]
                        
                        if len(parts) > 1 and any(ind in parts[0].lower() for ind in seo_indicators) and not any(ind in parts[-1].lower() for ind in seo_indicators):
                            suggested_name = parts[-1]
                            suggested_tagline = parts[0]
                        else:
                            suggested_name = parts[0] if parts else title
                            suggested_tagline = parts[1] if len(parts) > 1 else None

                        suggestions.append(
                            AutofillSuggestion(
                                field="name",
                                suggested_value=suggested_name,
                                source_url=safe_url,
                            )
                        )
                        if suggested_tagline:
                            suggestions.append(
                                AutofillSuggestion(
                                    field="tagline",
                                    suggested_value=suggested_tagline,
                                    source_url=safe_url,
                                )
                            )

                    # Extract meta description
                    desc_match = re.search(
                        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
                        html,
                        re.IGNORECASE | re.DOTALL,
                    )
                    if desc_match:
                        description = desc_match.group(1).strip()
                        suggestions.append(
                            AutofillSuggestion(
                                field="description",
                                suggested_value=description,
                                source_url=safe_url,
                            )
                        )

                    # Detect domains and city from text
                    combined_text = f"{title or ''} {description or ''}"
                    possible_domains = [
                        "Digital marketing",
                        "SEO",
                        "Paid ads",
                        "Social media marketing",
                        "Branding",
                        "Content strategy",
                        "AI",
                        "UI/UX",
                        "Web development",
                    ]
                    matched_domains = [
                        d for d in possible_domains if re.search(r"\b" + re.escape(d.split()[0]) + r"\b", combined_text, re.IGNORECASE)
                    ]
                    if matched_domains:
                        suggestions.append(
                            AutofillSuggestion(
                                field="domains",
                                suggested_value=", ".join(matched_domains),
                                source_url=safe_url,
                            )
                        )

                    # Detect city
                    for city_candidate in ["Coimbatore", "Chennai", "Bangalore", "Bengaluru", "Hyderabad", "Mumbai", "Delhi"]:
                        if re.search(r"\b" + re.escape(city_candidate) + r"\b", combined_text, re.IGNORECASE):
                            suggestions.append(
                                AutofillSuggestion(
                                    field="city",
                                    suggested_value=city_candidate,
                                    source_url=safe_url,
                                )
                            )
                            break

                    # Search social links
                    social_patterns = {
                        "facebook": r'href=["\'](https?://(?:www\.)?facebook\.com/[^"\']+)["\']',
                        "instagram": r'href=["\'](https?://(?:www\.)?instagram\.com/[^"\']+)["\']',
                        "youtube": r'href=["\'](https?://(?:www\.)?youtube\.com/[^"\']+)["\']',
                        "linkedin": r'href=["\'](https?://(?:www\.)?linkedin\.com/company/[^"\']+)["\']',
                    }
                    for platform, pat in social_patterns.items():
                        match = re.search(pat, html, re.IGNORECASE)
                        if match:
                            suggestions.append(
                                AutofillSuggestion(
                                    field=f"social_{platform}",
                                    suggested_value=match.group(1),
                                    source_url=safe_url,
                                )
                            )
        except Exception as e:
            logger.warning(f"Website autofill crawl failed for {safe_url}: {e}")

        return AutofillResponse(
            website_title=title,
            website_description=description,
            suggestions=suggestions,
        )

