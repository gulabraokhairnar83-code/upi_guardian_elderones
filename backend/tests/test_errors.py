"""Test centralized error handling."""


def test_404_not_found(client):
    response = client.get("/api/non-existent-endpoint")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_405_method_not_allowed(client):
    response = client.post("/api/health")
    assert response.status_code == 405
    data = response.get_json()
    assert "error" in data
