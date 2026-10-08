"""UPI Guardian - Phase 7 Full E2E Integration Verification Script.
Simulates all API requests made by the frontend in real API mode.
"""

import sys
import json
from datetime import datetime, timezone

sys.path.insert(0, r"c:\Users\Dell\Documents\UPI Guardian\backend")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from app import create_app

def run_tests():
    app = create_app("testing")
    client = app.test_client()

    print("=" * 70)
    print("UPI GUARDIAN — PHASE 7 FULL E2E INTEGRATION VERIFICATION")
    print("=" * 70)

    # 1. Health Check
    print("\n[1] Testing GET /api/health...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    health_data = res.get_json()
    print(f"Status: {health_data.get('status')}, Service: {health_data.get('service')}")
    assert health_data.get("status") in ("healthy", "degraded")

    # 2. Dashboard Summary
    print("\n[2] Testing GET /api/dashboard/summary...")
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    dash_data = res.get_json()
    print(f"Account Status: {dash_data.get('accountStatus')}")
    print(f"Current Risk Score: {dash_data.get('currentRiskScore')}")
    print(f"KPI Count: {len(dash_data.get('kpis', []))}")
    print(f"Recent Alerts Count: {len(dash_data.get('recentAlerts', []))}")
    assert "kpis" in dash_data
    assert "activity" in dash_data
    assert "overall_risk_score" in dash_data

    # 3. Transactions Listing & Detail
    print("\n[3] Testing GET /api/transactions...")
    res = client.get("/api/transactions")
    assert res.status_code == 200
    txns = res.get_json()
    print(f"Retrieved {len(txns)} transactions from MongoDB/mock repository.")
    assert len(txns) > 0
    sample_id = txns[0]["id"]

    print(f"Testing GET /api/transactions/{sample_id}...")
    res_single = client.get(f"/api/transactions/{sample_id}")
    assert res_single.status_code == 200
    single_txn = res_single.get_json()
    print(f"Transaction Payee: {single_txn.get('payee')}, Amount: {single_txn.get('amount')}")
    assert single_txn["id"] == sample_id

    # 4. ML Transaction Analysis
    print("\n[4] Testing POST /api/analyze-transaction...")
    tx_payload = {
        "payee": "Unknown Merchant",
        "amount": 42000,
        "upiId": "unknown@okaxis",
        "user_id": "usr_sunita_68"
    }
    res_anl = client.post("/api/analyze-transaction", json=tx_payload)
    assert res_anl.status_code == 200
    ml_res = res_anl.get_json()
    print(f"ML Risk Score: {ml_res.get('riskScore')}, Risk Level: {ml_res.get('riskLevel')}")
    assert "riskScore" in ml_res or "anomaly_score" in ml_res.get("analysis", {})
    assert "explanation" in ml_res

    # 5. SMS Scam Analyzer (NLP)
    print("\n[5] Testing POST /api/analyze-message (SMS)...")
    sms_payload = {
        "text": "Your electricity connection will be disconnected tonight. Call immediately to update KYC and make payment.",
        "message_type": "sms",
        "user_id": "usr_sunita_68"
    }
    res_sms = client.post("/api/analyze-message", json=sms_payload)
    assert res_sms.status_code == 200
    sms_res = res_sms.get_json()
    print(f"Scam Classification: {sms_res.get('analysis', {}).get('classification')}")
    print(f"Scam Probability   : {sms_res.get('analysis', {}).get('scam_probability')}%")
    print(f"Risk Level         : {sms_res.get('level')}")
    print(f"Detected Phrases   : {sms_res.get('analysis', {}).get('suspicious_phrases')}")
    assert sms_res.get("level") in ("high", "critical", "review")
    assert "potential scam" in sms_res.get("title", "").lower() or "suspicious" in sms_res.get("title", "").lower()

    # 6. Call Scam Analyzer (NLP)
    print("\n[6] Testing POST /api/analyze-message (Call Transcript)...")
    call_payload = {
        "text": "Sir, this is inspector Sharma from Crime Branch. A digital warrant is issued against you. Transfer penalty money immediately to secure your arrest cancellation.",
        "message_type": "call_transcript",
        "user_id": "usr_sunita_68"
    }
    res_call = client.post("/api/analyze-message", json=call_payload)
    assert res_call.status_code == 200
    call_res = res_call.get_json()
    print(f"Call Classification: {call_res.get('analysis', {}).get('classification')}")
    print(f"Call Risk Level    : {call_res.get('level')}")
    assert call_res.get("level") in ("high", "critical")

    # 7. Risk Fusion Analysis (Phase 6)
    print("\n[7] Testing POST /api/risk/analyze (Phase 6 Risk Fusion)...")
    fusion_payload = {
        "transaction_id": "TXN-UG-FUSION-001",
        "user_id": "usr_sunita_68",
        "payee": "Electricity Officer",
        "amount": 35000,
        "upiId": "officer@okaxis",
        "is_new_payee": True,
        "velocity": 3
    }
    res_fusion = client.post("/api/risk/analyze", json=fusion_payload)
    assert res_fusion.status_code == 200
    fusion_raw = res_fusion.get_json()
    assert fusion_raw.get("success") is True
    fusion_res = fusion_raw["analysis"]
    print(f"Final Risk Score         : {fusion_res.get('final_risk_score')}")
    print(f"Risk Level               : {fusion_res.get('risk_level')}")
    print(f"Transaction Anomaly Score: {fusion_res.get('transaction_anomaly_score')}")
    print(f"Communication Risk Score : {fusion_res.get('communication_risk_score')}")
    print(f"Temporal Correlation     : {fusion_res.get('temporal_correlation_score')}")
    print(f"Correlation Boost        : {fusion_res.get('correlation_boost')}")
    print(f"Top Factors              : {fusion_res.get('top_contributing_factors')}")
    print(f"Recommended Action       : {fusion_res.get('recommended_action')}")
    assert "final_risk_score" in fusion_res
    assert "top_contributing_factors" in fusion_res

    # 8. Risk Events
    print("\n[8] Testing GET /api/risk/events...")
    res_events = client.get("/api/risk/events?user_id=usr_sunita_68")
    assert res_events.status_code == 200
    events_raw = res_events.get_json()
    events = events_raw.get("events", [])
    print(f"Retrieved {len(events)} risk events.")
    assert isinstance(events, list)

    # 9. Alerts & Alert Resolve
    print("\n[9] Testing GET /api/alerts and POST /api/alerts/<id>/resolve...")
    res_alerts = client.get("/api/alerts")
    assert res_alerts.status_code == 200
    alerts = res_alerts.get_json()
    print(f"Retrieved {len(alerts)} alerts.")
    if alerts:
        target_alert_id = alerts[0]["id"]
        res_resolve = client.post(f"/api/alerts/{target_alert_id}/resolve")
        assert res_resolve.status_code == 200
        resolve_data = res_resolve.get_json()
        print(f"Resolved alert {target_alert_id}: success={resolve_data.get('success')}")

    # 10. Settings GET & PATCH Persistence
    print("\n[10] Testing GET /api/settings and PATCH /api/settings...")
    res_settings = client.get("/api/settings")
    assert res_settings.status_code == 200
    init_settings = res_settings.get_json()
    print(f"Current Profile Name: {init_settings.get('profile', {}).get('name')}")

    patch_payload = {
        "profile": {"name": "Sunita Devi Verified", "age": 68},
        "accessibility": {"seniorMode": True}
    }
    res_patch = client.patch("/api/settings", json=patch_payload)
    assert res_patch.status_code == 200
    updated_settings = res_patch.get_json()
    print(f"Updated Profile Name: {updated_settings.get('profile', {}).get('name')}")
    assert updated_settings.get("profile", {}).get("name") == "Sunita Devi Verified"

    # 11. Family Profile
    print("\n[11] Testing GET /api/family/profile...")
    res_family = client.get("/api/family/profile")
    assert res_family.status_code == 200
    fam_data = res_family.get_json()
    print(f"Elder Profile Name: {fam_data.get('name')}")
    print(f"Account Safety    : {fam_data.get('accountSafetyStatus')}")
    print(f"Metrics           : {fam_data.get('metrics')}")
    assert "name" in fam_data
    assert "metrics" in fam_data

    print("\n" + "=" * 70)
    print("ALL 11 INTEGRATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
