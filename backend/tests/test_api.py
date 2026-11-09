import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from tests.conftest import TestingSessionLocal as SessionLocal
from app.models.competitor import Competitor
from app.models.ad import Ad
from app.core.security import validate_target_url
from fastapi import HTTPException


@pytest.fixture(scope="module")
def client():
    # Setup test database records
    db = SessionLocal()
    try:
        sample_competitors = [
            ("Nexora Academy", "Coimbatore", "AI", "page_nexora_coimbatore", "high"),
            ("Growth Lab", "Coimbatore", "Digital marketing", "page_growthlab_cbe", "high"),
            ("Lumen Design School", "Coimbatore", "UI/UX", "page_lumen_design", "high"),
            ("CodeBridge Institute", "Coimbatore", "AI", "page_codebridge_cbe", "high"),
            ("Pixel & Pen Institute", "Coimbatore", "UI/UX", "page_pixelpen_cbe", "needs_review"),
            ("Skillhub Tech", "Coimbatore", "Digital marketing", "page_skillhub_tech", "high"),
        ]
        for name, city, course, page_id, conf in sample_competitors:
            existing = db.query(Competitor).filter(Competitor.name == name).first()
            if not existing:
                comp = Competitor(
                    name=name,
                    city=city,
                    course=course,
                    fb_page_id=page_id,
                    confidence=conf,
                    is_active=True,
                )
                db.add(comp)
                db.flush()
                # Add sample ad for testing
                ad = Ad(
                    ad_archive_id=f"test_archive_{comp.id}",
                    competitor_id=comp.id,
                    source="test_source",
                    copy=f"Learn {course} at {name}",
                    headline=f"Master {course}",
                    cta="Apply now",
                    platforms_str="facebook,instagram",
                    start_date="2026-01-01",
                    is_active=True,
                    first_seen=datetime.now(timezone.utc).replace(tzinfo=None),
                    last_seen=datetime.now(timezone.utc).replace(tzinfo=None),
                    run_days=comp.id * 10,
                )
                db.add(ad)
        db.commit()
    finally:
        db.close()

    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_v1_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "active_providers_count" in data


def test_get_competitors(client):
    response = client.get("/api/v1/competitors")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 6
    names = [c["name"] for c in data]
    assert "Nexora Academy" in names
    assert "Growth Lab" in names


def test_get_ads(client):
    response = client.get("/api/v1/ads?sort_by=days")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 6
    days = [a["run_days"] for a in data]
    assert days == sorted(days, reverse=True)


def test_get_market_insights(client):
    response = client.get("/api/v1/ads/insights/market?city=Coimbatore")
    assert response.status_code == 200
    data = response.json()
    assert "headline" in data
    assert "subline" in data
    assert "top_hook" in data
    assert "gap_course" in data


def test_discover_competitors(client):
    payload = {"city": "Coimbatore", "query": "AI", "limit": 5}
    response = client.post("/api/v1/competitors/discover", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any("AI" in item["course"] for item in data)


def test_resolve_page_id(client):
    # Meta Ad Library URL test
    url_payload = {"input_text": "https://www.facebook.com/ads/library/?view_all_page_id=1029384756"}
    res = client.post("/api/v1/competitors/resolve", json=url_payload)
    assert res.status_code == 200
    assert res.json()["resolved_page_id"] == "1029384756"
    assert res.json()["confidence"] == "high"


def test_generate_poster_prompt(client):
    ads_res = client.get("/api/v1/ads")
    ad_id = ads_res.json()[0]["id"]

    payload = {
        "ad_id": ad_id,
        "course": "AI",
        "angle_index": 0,
        "size_format": "feed",
    }
    response = client.post("/api/v1/posters/prompt", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Draw no lettering in the image" in data["prompt"]
    assert data["headline"] == "Build real AI projects in 12 weeks"
    assert data["cta_text"] == "Book a free demo"


def test_ssrf_protection():
    with pytest.raises(HTTPException):
        validate_target_url("http://127.0.0.1:8080/test")

    with pytest.raises(HTTPException):
        validate_target_url("http://192.168.1.1/admin")

    with pytest.raises(HTTPException):
        validate_target_url("https://malicious-domain.com/steal")
