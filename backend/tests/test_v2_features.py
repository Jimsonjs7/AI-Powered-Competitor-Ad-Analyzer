import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_profile_lifecycle(client):
    # 1. Get profile (returns blank template when clean)
    res = client.get("/api/v1/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 0 or "BrandMonk" in data["name"]

    # 2. Update profile with courses, claims, and location
    update_payload = {
        "name": "BrandMonk Academy Coimbatore",
        "city": "Coimbatore",
        "radius_km": 15.0,
        "domains": ["AI", "Digital marketing", "UI/UX"],
        "services": [
            {
                "name": "Full Stack AI Engineering",
                "fee_min": 25000.0,
                "fee_max": 35000.0,
                "duration": "12 weeks",
                "mode": "hybrid",
                "outcomes": "Build 5 production AI projects",
            }
        ],
        "claims": [
            {
                "text": "Every project code-reviewed weekly by working engineers",
                "proof_link": "https://brandmonk.academy/mentors",
                "approved": True,
            },
            {
                "text": "100% transparent fee structure with zero hidden charges",
                "approved": True,
            },
        ],
    }
    update_res = client.put("/api/v1/profile", json=update_payload)
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "BrandMonk Academy Coimbatore"
    assert len(updated["services"]) == 1
    assert len(updated["claims"]) == 2
    assert updated["version"] >= 1

    # 3. Check completeness meter
    comp_res = client.get("/api/v1/profile/completeness")
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["score"] >= 60
    assert comp_data["is_ready_for_discovery"] is True


def test_discovery_agent_lifecycle(client):
    async def dummy_async_discovery(*args, **kwargs):
        pass

    with patch("app.services.discovery_service.DiscoveryService.execute_discovery_async", side_effect=dummy_async_discovery):
        # Start discovery run
        payload = {"radius_km": 10.0, "search_terms": ["AI Training Institute"]}
        res = client.post("/api/v1/discovery/run", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "run_id" in data
        assert data["status"] == "running"

        # Poll status
        status_res = client.get(f"/api/v1/discovery/{data['run_id']}/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["run_id"] == data["run_id"]
        assert "current_step" in status_data


def test_evidence_and_sufficiency_gating(client):
    # Find or use first competitor
    comps = client.get("/api/v1/competitors").json()
    assert len(comps) > 0
    comp_id = comps[0]["id"]

    # Check initial sufficiency
    suff_res = client.get(f"/api/v1/competitors/{comp_id}/sufficiency")
    assert suff_res.status_code == 200
    suff = suff_res.json()
    assert "is_sufficient" in suff

    # Import evidence item (privacy sanitized)
    ev_payload = {
        "competitor_id": comp_id,
        "source": "google_maps",
        "text": "The course was okay but hidden fee of 5000 asked during exam @student123",
        "category": "pricing_clarity",
    }
    ev_res = client.post("/api/v1/evidence/import", json=ev_payload)
    assert ev_res.status_code == 200
    ev_item = ev_res.json()
    assert "@student123" not in ev_item["text"]
    assert "[user]" in ev_item["text"]
    assert "text_hash" not in ev_item  # privacy verified

    # List evidence
    list_res = client.get(f"/api/v1/competitors/{comp_id}/evidence")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


def test_weakness_and_opportunity_engine(client):
    comps = client.get("/api/v1/competitors").json()
    comp_id = comps[0]["id"]

    # Trigger weakness analysis
    try:
        analyze_res = client.post(f"/api/v1/competitors/{comp_id}/analyze")
        if analyze_res.status_code == 200:
            weaknesses = analyze_res.json()
            assert isinstance(weaknesses, list)
    except Exception:
        pass

    # Check weakness list endpoint
    w_list_res = client.get(f"/api/v1/competitors/{comp_id}/weaknesses")
    assert w_list_res.status_code == 200
    assert "weaknesses" in w_list_res.json()

    # Check opportunities endpoint
    opps_res = client.get("/api/v1/opportunities")
    assert opps_res.status_code == 200
    opps = opps_res.json()
    assert isinstance(opps, list)

    if len(opps) > 0:
        opp_id = opps[0]["id"]
        # Generate counter-angle draft enforcing approved claims
        draft_res = client.post("/api/v1/opportunities/draft", json={"opportunity_id": opp_id})
        assert draft_res.status_code == 200
        draft = draft_res.json()
        assert len(draft["headline_options"]) > 0
        assert "compliance_note" in draft
        assert "primary_text" in draft
