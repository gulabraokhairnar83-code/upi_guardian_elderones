"""Test /api/settings endpoints."""


def test_get_settings(client):
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.get_json()
    assert "profile" in data
    assert "security" in data
    assert "alertPreferences" in data
    assert "accessibility" in data


def test_patch_settings_success(client):
    update_payload = {
        "accessibility": {
            "seniorMode": True,
            "reducedMotion": True,
        }
    }
    response = client.patch("/api/settings", json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["accessibility"]["seniorMode"] is True
    assert data["accessibility"]["reducedMotion"] is True


def test_patch_settings_invalid(client):
    response = client.patch("/api/settings", json={"invalidSection": 123})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
