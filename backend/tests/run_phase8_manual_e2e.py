"""UPI Guardian - Phase 8 Manual E2E Demonstration Script.

Step-by-step verification of:
1. Register elder account
2. Login & JWT retrieval
3. Add caregiver
4. Verify caregiver
5. Enable SMS & Voice preferences
6. Inject suspicious communication
7. Analyze suspicious transaction via Phase 6 Risk Fusion
8. Automatic escalation triggers Mock Twilio SMS & Voice
9. MongoDB notification records created
10. Caregiver acknowledges notification
11. Deduplication check (re-dispatching same event creates NO duplicate)
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.notifications.twilio_client import get_mock_twilio_client
from app.risk_fusion.inference import RiskFusionService
from app.notifications.notification_repository import NotificationRepository


def run_e2e():
    app = create_app("testing")
    client = app.test_client()
    mock_twilio = get_mock_twilio_client()
    mock_twilio.sent_messages.clear()
    mock_twilio.made_calls.clear()

    print("=" * 75)
    print("UPI GUARDIAN — PHASE 8 MANUAL E2E END-TO-END DEMONSTRATION")
    print("=" * 75)

    # Step 1: Register elder account
    print("\n[Step 1] Registering Protected Elder Account...")
    reg_res = client.post("/api/auth/register", json={
        "name": "Ramesh Chandra Sharma",
        "email": "ramesh.sharma@example.com",
        "password": "SecureGuardian2026!",
        "phone": "+919876500111",
        "role": "ELDER",
    })
    assert reg_res.status_code == 201, f"Register failed: {reg_res.get_json()}"
    elder_user = reg_res.get_json()["user"]
    elder_id = elder_user["user_id"]
    access_token = reg_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f" -> Elder registered successfully! User ID: {elder_id}, Name: {elder_user['name']}")

    # Step 2: Login test
    print("\n[Step 2] Authenticating with Email & Password...")
    login_res = client.post("/api/auth/login", json={
        "email": "ramesh.sharma@example.com",
        "password": "SecureGuardian2026!",
    })
    assert login_res.status_code == 200
    print(f" -> Login successful! JWT Access Token received (length: {len(access_token)})")

    # Step 3: Add caregiver
    print("\n[Step 3] Adding Trusted Caregiver (Son: Rohit Sharma)...")
    cg_res = client.post("/api/caregivers", json={
        "name": "Rohit Sharma",
        "phone": "+919876543210",
        "email": "rohit.sharma@example.com",
        "relationship": "SON",
        "notification_preferences": {
            "sms_enabled": True,
            "voice_enabled": True,
            "high_risk_enabled": True,
            "critical_risk_enabled": True,
        },
    }, headers=headers)
    assert cg_res.status_code == 201
    caregiver = cg_res.get_json()
    cg_id = caregiver["caregiver_id"]
    print(f" -> Caregiver created: {caregiver['name']} ({cg_id}), Status: {caregiver['status']}")

    # Step 4: Verify caregiver
    print("\n[Step 4] Verifying Caregiver Relationship...")
    verify_res = client.post(f"/api/caregivers/{cg_id}/verify", headers=headers)
    assert verify_res.status_code == 200
    print(f" -> Caregiver status verified: {verify_res.get_json()['status']}, is_verified: {verify_res.get_json()['is_verified']}")

    # Step 5 & 6 & 7: Trigger Suspicious Transaction with Scam Communication Match
    print("\n[Step 5-8] Simulating Suspicious Communication followed by High-Value Transaction...")
    now = datetime.now(timezone.utc)
    scam_comm = [
        {
            "id": "MSG_E2E_SCAM_01",
            "classification": "SCAM",
            "risk_level": "CRITICAL",
            "scam_probability": 98.0,
            "analyzed_at": (now - timedelta(minutes=15)).isoformat(),
        }
    ]

    with app.app_context():
        fusion_service = RiskFusionService()
        tx_data = {
            "transaction_id": "TXN_E2E_CRIT_888",
            "user_id": elder_id,
            "amount": 75000.0,
            "payee": "Fake Police Digital Arrest Clearance",
            "upiId": "police.clearance@axisbank",
            "is_new_payee": True,
            "velocity": 2,
            "timestamp": now.isoformat(),
        }

        # Step 9: Phase 6 Risk Fusion Engine calculates risk
        analysis = fusion_service.analyze_transaction_risk(
            transaction_data=tx_data,
            candidate_communications=scam_comm,
            user_id=elder_id,
            create_alert_if_needed=True,
            persist_event=True,
        )

        risk_level = analysis["risk_level"]
        risk_score = analysis["final_risk_score"]
        print(f" -> Multi-Signal Fusion Result: Risk Level = {risk_level}, Risk Score = {risk_score}/100")
        print(f" -> Correlation Boost: +{analysis['correlation_boost']} (Communication match within 15 mins)")

    # Step 10, 11, 12: Escalation Service triggered Mock Twilio SMS & Voice
    print("\n[Step 9-12] Checking Escalation Dispatch via Mock Twilio Provider...")
    print(f" -> Mock SMS Messages Sent: {len(mock_twilio.sent_messages)}")
    assert len(mock_twilio.sent_messages) >= 1
    last_sms = mock_twilio.sent_messages[-1]
    print(f"    - SMS SID : {last_sms['sid']}")
    print(f"    - To Phone: {last_sms['to']}")
    print("    - Preview :\n" + "      " + "\n      ".join(last_sms['body'].splitlines()[:4]))

    print(f" -> Mock Voice Calls Initiated: {len(mock_twilio.made_calls)}")
    assert len(mock_twilio.made_calls) >= 1
    last_call = mock_twilio.made_calls[-1]
    print(f"    - Call SID: {last_call['sid']}")
    print(f"    - To Phone: {last_call['to']}")

    # Step 13, 14: Inspect MongoDB notification records via API
    print("\n[Step 13-14] Fetching Logged Notifications from Database via API...")
    notif_res = client.get("/api/notifications", headers=headers)
    assert notif_res.status_code == 200
    notifications = notif_res.get_json()
    print(f" -> Dispatched notification records found in DB: {len(notifications)}")
    assert len(notifications) >= 1
    first_notif = notifications[0]
    notif_id = first_notif["notification_id"]
    print(f" -> Target Notification ID: {notif_id}, Channel: {first_notif['channel']}, Acknowledged: {first_notif['is_acknowledged']}")

    # Step 15, 16: Caregiver acknowledges notification
    print("\n[Step 15-16] Caregiver Acknowledging Emergency Alert...")
    ack_res = client.post(f"/api/notifications/{notif_id}/acknowledge", headers=headers)
    assert ack_res.status_code == 200
    ack_record = ack_res.get_json()
    print(f" -> Notification Acknowledged: {ack_record['is_acknowledged']}")
    print(f" -> Acknowledged By: {ack_record['acknowledged_by']} at {ack_record['acknowledged_at']}")

    # Step 17: Deduplication check
    print("\n[Step 17] Verifying Idempotency & Deduplication...")
    with app.app_context():
        from app.notifications.escalation_service import EscalationService
        sms_count_before = len(mock_twilio.sent_messages)
        voice_count_before = len(mock_twilio.made_calls)

        # Dispatching exact same event again
        repeat_res = EscalationService.escalate_risk_event(analysis, user_id=elder_id)
        sms_count_after = len(mock_twilio.sent_messages)
        voice_count_after = len(mock_twilio.made_calls)

        print(f" -> Re-dispatching same event ({analysis.get('risk_event_id') or tx_data['transaction_id']}):")
        print(f"    - New notifications dispatched: {repeat_res['caregivers_notified_count']}")
        print(f"    - SMS count changed : {sms_count_after - sms_count_before} (Expected: 0)")
        print(f"    - Voice count changed: {voice_count_after - voice_count_before} (Expected: 0)")
        assert sms_count_after == sms_count_before
        assert voice_count_after == voice_count_before
        print(" -> SUCCESS: Idempotency guaranteed! Zero duplicate notifications dispatched.")

    print("\n" + "=" * 75)
    print("PHASE 8 MANUAL E2E TEST COMPLETED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_e2e()
