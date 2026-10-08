import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta, timezone
from app import create_app
from app.risk_fusion.inference import RiskFusionService

app = create_app()
client = app.test_client()

now = datetime.now(timezone.utc)

print("=" * 65)
print("TEST 1: Normal transaction + no communication")
print("=" * 65)
r1 = client.post("/api/risk/analyze", json={
    "user_id": "usr_sunita_68",
    "payee": "Sharma General Store",
    "amount": 2500,
    "upiId": "sharma.store@okaxis",
    "is_new_payee": False,
})
d1 = r1.get_json()["analysis"]
print(f"Final Score: {d1['final_risk_score']}")
print(f"Risk Level:  {d1['risk_level']}")
print(f"Boost:       {d1['correlation_boost']}")
print(f"Action:      {d1['recommended_action']}")

print("\n" + "=" * 65)
print("TEST 2: Large unusual transaction + new payee + no communication")
print("=" * 65)
r2 = client.post("/api/risk/analyze", json={
    "user_id": "usr_sunita_68",
    "payee": "Unknown New Merchant",
    "amount": 45000,
    "upiId": "unknown@upi",
    "is_new_payee": True,
    "velocity": 3,
})
d2 = r2.get_json()["analysis"]
print(f"Final Score: {d2['final_risk_score']}")
print(f"Risk Level:  {d2['risk_level']}")
print(f"Factors:     {d2['top_contributing_factors']}")
print(f"Action:      {d2['recommended_action']}")

print("\n" + "=" * 65)
print("TEST 3: Scam SMS + no transaction")
print("=" * 65)
r3 = client.post("/api/analyze-message", json={
    "user_id": "usr_sunita_68",
    "text": "Your SBI account is blocked. Update KYC immediately at http://sbi-verify.apk or service will stop.",
    "message_type": "sms",
})
d3 = r3.get_json()["analysis"]
print(f"Classification:   {d3['classification']}")
print(f"Scam Probability: {d3['scam_probability']}%")
print(f"Risk Level:       {d3['risk_level']}")
print(f"Explanation:      {d3['explanation']}")

print("\n" + "=" * 65)
print("TEST 4: Scam SMS + Large unusual transaction + within 2 hours")
print("=" * 65)
# Message analyzed just now
client.post("/api/analyze-message", json={
    "user_id": "usr_sunita_68",
    "text": "Your electricity power will be disconnected tonight at 9:30 PM. Pay bill urgently to avoid disconnection.",
    "message_type": "sms",
})
r4 = client.post("/api/risk/analyze", json={
    "user_id": "usr_sunita_68",
    "payee": "Electricity Collection Officer",
    "amount": 48000,
    "upiId": "elec.officer@okaxis",
    "is_new_payee": True,
    "velocity": 3,
    "timestamp": now.isoformat(),
})
d4 = r4.get_json()["analysis"]
print(f"Tx Anomaly Score:  {d4['transaction_anomaly_score']}")
print(f"Comm Risk Score:   {d4['communication_risk_score']}")
print(f"Temporal Corr:     {d4['temporal_correlation_score']}")
print(f"Correlation Boost: {d4['correlation_boost']}")
print(f"Final Risk Score:  {d4['final_risk_score']}")
print(f"Risk Level:        {d4['risk_level']}")
print(f"Alert Created:     {d4['alert_created']}")
print(f"Factors:           {d4['top_contributing_factors']}")

print("\n" + "=" * 65)
print("TEST 5: Scam SMS + Unusual transaction + older than 2 hours (5 hours before)")
print("=" * 65)
service = RiskFusionService()
old_comm = [{
    "id": "msg_old_01",
    "classification": "SCAM",
    "risk_level": "CRITICAL",
    "scam_probability": 95.0,
    "analyzed_at": (now - timedelta(minutes=300)).isoformat(),
}]
d5 = service.analyze_transaction_risk(
    transaction_data={
        "user_id": "usr_sunita_68",
        "payee": "Some Store",
        "amount": 25000,
        "upiId": "store@upi",
        "timestamp": now.isoformat(),
    },
    candidate_communications=old_comm,
)
print(f"Comm Risk Score:   {d5['communication_risk_score']}")
print(f"Temporal Corr:     {d5['temporal_correlation_score']}")
print(f"Correlation Boost: {d5['correlation_boost']}")
print(f"Final Risk Score:  {d5['final_risk_score']}")
print(f"Risk Level:        {d5['risk_level']}")
print("=" * 65)
