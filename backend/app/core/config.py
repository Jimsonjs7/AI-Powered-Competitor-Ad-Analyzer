import json
from typing import Any, List, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Ad Desk - BrandMonk Ad Analyzer"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    allowed_origins_raw: Union[List[str], str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        alias="allowed_origins",
    )

    @property
    def allowed_origins(self) -> List[str]:
        v = self.allowed_origins_raw
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Security tokens
    api_bearer_token: str = Field(default="dev-insecure-token-brandmonk")
    jwt_secret: str = Field(default="dev-insecure-jwt-secret-replace-in-prod")

    # Database
    database_url: str = Field(default="sqlite:///./brandmonk.db")

    # Scraping limits and timeouts
    monthly_cost_cap_usd: float = 10.0
    scrape_timeout_seconds: int = 120
    min_seconds_between_requests: float = 2.0
    media_storage_dir: str = "./media_storage"

    # External Provider Credentials (with multi-key failover pool)
    apify_api_token: str | None = None
    apify_api_token_2: str | None = None
    apify_api_token_3: str | None = None
    apify_api_tokens: str | None = None
    apify_meta_actor_id: str = "jaybird~meta-ad-library-scraper"
    apify_maps_actor_id: str = "compass/crawler-google-places"
    scrapecreators_api_key: str | None = None
    serpapi_api_key: str | None = None
    google_places_api_key: str | None = None

    # AI Multimodal Keys (with multi-key failover pool)
    gemini_api_key: str | None = None
    gemini_api_key_2: str | None = None
    gemini_api_key_3: str | None = None
    gemini_api_keys: str | None = None
    anthropic_api_key: str | None = None
    image_generation_api_key: str | None = None

    @property
    def all_apify_api_tokens(self) -> List[str]:
        tokens: List[str] = []
        if self.apify_api_tokens:
            tokens.extend([t.strip() for t in self.apify_api_tokens.split(",") if t.strip()])
        for single in [self.apify_api_token, self.apify_api_token_2, self.apify_api_token_3]:
            if single and single.strip() and single.strip() not in tokens:
                tokens.append(single.strip())
        return tokens

    @property
    def all_gemini_api_keys(self) -> List[str]:
        keys: List[str] = []
        if self.gemini_api_keys:
            keys.extend([k.strip() for k in self.gemini_api_keys.split(",") if k.strip()])
        for single in [self.gemini_api_key, self.gemini_api_key_2, self.gemini_api_key_3]:
            if single and single.strip() and single.strip() not in keys:
                keys.append(single.strip())
        return keys

    # SSRF protection: strict allowed target host list
    ssrf_allowed_hosts: List[str] = [
        "facebook.com",
        "www.facebook.com",
        "web.facebook.com",
        "m.facebook.com",
        "instagram.com",
        "www.instagram.com",
        "adstransparency.google.com",
    ]


settings = Settings()

