from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Ad Desk - BrandMonk Ad Analyzer"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

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

    # External Provider Credentials
    apify_api_token: str | None = None
    apify_meta_actor_id: str = "apify/meta-ad-library-scraper"
    apify_maps_actor_id: str = "compass/crawler-google-places"
    scrapecreators_api_key: str | None = None
    serpapi_api_key: str | None = None
    google_places_api_key: str | None = None

    # AI Multimodal and Image Keys
    gemini_api_key: str | None = None
    anthropic_api_key: str | None = None
    image_generation_api_key: str | None = None

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
