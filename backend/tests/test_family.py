"""Test /api/family endpoints."""


def test_get_family_profile(client):
    response = client.get("/api/family/profile")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Sunita Devi"
    assert data["age"] == 68
    assert "metrics" in data
    assert "currentRiskScore" in data["metrics"]


def test_resolve_family_alerts(client):
    response = client.post("/api/family/alerts/resolve")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["profile"]["metrics"]["activeAlertsCount"] == 0
