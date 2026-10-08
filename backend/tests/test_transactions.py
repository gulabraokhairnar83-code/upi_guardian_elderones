"""Test /api/transactions endpoints."""


def test_list_transactions(client):
    response = client.get("/api/transactions")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 24


def test_filter_transactions_by_status(client):
    response = client.get("/api/transactions?status=critical")
    assert response.status_code == 200
    data = response.get_json()
    assert all(t["status"] == "critical" for t in data)


def test_search_transactions_by_query(client):
    response = client.get("/api/transactions?q=Rahul")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert any("Rahul" in t["payee"] for t in data)


def test_get_single_transaction_found(client):
    response = client.get("/api/transactions/TXN-UG-928401")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == "TXN-UG-928401"
    assert "payee" in data
    assert "amount" in data


def test_get_single_transaction_not_found(client):
    response = client.get("/api/transactions/TXN-UNKNOWN-999999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_analyze_transaction_success(client):
    payload = {
        "payee": "Test Merchant",
        "amount": 25000,
        "upiId": "merchant@upi",
    }
    response = client.post("/api/analyze-transaction", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["payee"] == "Test Merchant"
    assert data["amount"] == 25000
    assert "analysis" in data
    assert "anomaly_score" in data["analysis"]
    assert 0 <= data["analysis"]["anomaly_score"] <= 100
    assert data["analysis"]["model_version"] == "1.0.0"
    assert "features" in data["analysis"]
    assert "explanation" in data
    assert "riskScore" in data
    assert "riskLevel" in data


def test_analyze_transaction_invalid_payload(client):
    # Missing payee and amount
    response = client.post("/api/analyze-transaction", json={"upiId": "test@upi"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
