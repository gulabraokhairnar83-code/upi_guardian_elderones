"""Test /api/dashboard/summary endpoint."""


def test_dashboard_summary(client):
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.get_json()
    assert "systemStatus" in data
    assert data["systemStatus"] == "OPERATIONAL"
    assert "currentRiskScore" in data
    assert isinstance(data["currentRiskScore"], (int, float))
    assert "kpis" in data
    assert len(data["kpis"]) >= 6
    assert "activity" in data
    assert "recentAlerts" in data
