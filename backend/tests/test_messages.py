"""Test /api/analyze-message endpoint."""


def test_analyze_message_sms_success(client):
    payload = {
        "text": "URGENT: Your account will be blocked. Share OTP to prevent block.",
        "type": "sms",
    }
    response = client.post("/api/analyze-message", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["isSuspicious"] is True
    assert data["analysis"]["classification"] in ("SCAM", "SUSPICIOUS")
    assert "explanation" in data
    assert "recommendations" in data


def test_analyze_message_call_success(client):
    payload = {
        "text": "Your electricity connection will be cut off today unless you pay immediately.",
        "type": "call",
    }
    response = client.post("/api/analyze-message", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["isSuspicious"] is True
    assert "ELECTRICITY_DISCONNECTION_SCAM" in data["analysis"]["categories"]


def test_analyze_message_missing_text(client):
    response = client.post("/api/analyze-message", json={"type": "sms"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_analyze_message_invalid_type(client):
    response = client.post(
        "/api/analyze-message",
        json={"text": "hello scam test", "type": "whatsapp"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
