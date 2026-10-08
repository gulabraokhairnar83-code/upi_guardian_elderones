"""Test /api/health endpoint."""


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "upi-guardian-backend"
    assert data["version"] == "1.0.0"
