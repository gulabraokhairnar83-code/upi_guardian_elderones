"""Test /api/alerts endpoints."""


def test_list_alerts(client):
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_filter_alerts_by_level(client):
    response = client.get("/api/alerts?level=critical")
    assert response.status_code == 200
    data = response.get_json()
    assert all(a["level"] == "critical" for a in data)


def test_resolve_alert_success(client):
    response = client.post("/api/alerts/1/resolve")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["id"] == 1


def test_resolve_alert_not_found(client):
    response = client.post("/api/alerts/9999/resolve")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_resolve_alert_invalid_id(client):
    response = client.post("/api/alerts/abc/resolve")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
