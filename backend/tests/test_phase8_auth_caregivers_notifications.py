"""UPI Guardian - Phase 8 Unit and Integration Tests.

Comprehensive tests covering:
- Authentication & JWT security (register, login, refresh, logout, password hashing)
- Caregiver management & ownership isolation (CRUD, verification, permissions)
- Twilio notification services (Mock provider, SMS, Voice)
- Risk fusion escalation triggers (LOW, MEDIUM, HIGH, CRITICAL)
- Notification deduplication, quiet hours, and hourly rate limiting
- Caregiver acknowledgement and authorization checks
- Privacy & safety wording enforcement
"""

import json
import pytest
from app.notifications.twilio_client import get_mock_twilio_client
from app.notifications.message_builder import (
    mask_phone_number,
    mask_recipient,
    build_caregiver_sms_text,
    build_caregiver_voice_twiml,
)
from app.notifications.escalation_service import EscalationService, is_in_quiet_hours
from app.notifications.notification_repository import NotificationRepository


# =====================================================================
# 1. AUTHENTICATION TESTS
# =====================================================================

def test_01_auth_register_success(client):
    """Register new elder user successfully."""
    payload = {
        "email": "test_elder_1@example.com",
        "password": "StrongPassword123!",
        "name": "Elder Rameshwar",
        "phone": "+919876543210",
        "role": "ELDER",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data["user"]["email"] == "test_elder_1@example.com"
    # Security: No password or password_hash leaked
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_02_auth_register_duplicate_email(client):
    """Registration with an already existing email returns 409 Conflict."""
    payload = {
        "email": "test_elder_dup@example.com",
        "password": "StrongPassword123!",
        "name": "Original User",
        "role": "ELDER",
    }
    # First registration
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Second registration with same email
    res2 = client.post("/api/auth/register", json={
        "email": "test_elder_dup@example.com",
        "password": "AnotherPassword123!",
        "name": "Duplicate User",
        "role": "ELDER",
    })
    assert res2.status_code == 409


def test_03_auth_login_success(client):
    """Login with valid credentials returns tokens."""
    # Register user first
    reg = client.post("/api/auth/register", json={
        "email": "test_elder_login@example.com",
        "password": "StrongPassword123!",
        "name": "Elder Rameshwar",
    })
    assert reg.status_code == 201

    payload = {
        "email": "test_elder_login@example.com",
        "password": "StrongPassword123!",
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["name"] == "Elder Rameshwar"
    assert "password_hash" not in data["user"]


def test_04_auth_login_invalid_password(client):
    """Login with invalid password returns 401 Unauthorized."""
    # Register user first
    client.post("/api/auth/register", json={
        "email": "test_elder_inv@example.com",
        "password": "StrongPassword123!",
        "name": "Elder Inv",
    })

    payload = {
        "email": "test_elder_inv@example.com",
        "password": "WrongPassword999!",
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 401


def test_05_auth_login_nonexistent_user(client):
    """Login for non-existent user returns 401 Unauthorized."""
    payload = {
        "email": "nonexistent_user@example.com",
        "password": "Password123!",
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 401


def test_06_protected_route_without_token(client):
    """Accessing protected endpoint without Bearer token returns 401."""
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_07_protected_route_with_valid_token(client):
    """Accessing protected endpoint with valid JWT returns current user."""
    # Register to get token
    reg = client.post("/api/auth/register", json={
        "email": "test_elder_me@example.com",
        "password": "StrongPassword123!",
        "name": "Elder Me",
    })
    token = reg.get_json()["access_token"]

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"]["email"] == "test_elder_me@example.com"
    assert "password_hash" not in data["user"]


def test_08_auth_refresh_token(client):
    """Refresh endpoint exchanges refresh_token for new access token."""
    reg = client.post("/api/auth/register", json={
        "email": "test_elder_ref@example.com",
        "password": "StrongPassword123!",
        "name": "Elder Ref",
    })
    refresh_token = reg.get_json()["refresh_token"]

    res = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data


def test_09_auth_logout_revokes_token(client):
    """Logout blacklists active token on server so reuse fails."""
    reg = client.post("/api/auth/register", json={
        "email": "test_elder_logout@example.com",
        "password": "StrongPassword123!",
        "name": "Elder Logout",
    })
    token = reg.get_json()["access_token"]

    # Logout
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200

    # Attempt to reuse logged out token
    subsequent_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert subsequent_res.status_code == 401


# =====================================================================
# 2. CAREGIVER MANAGEMENT TESTS
# =====================================================================

def test_10_caregiver_crud_lifecycle(client):
    """Full lifecycle for caregiver: create, list, get, update preferences, delete."""
    # Register Elder A
    reg_a = client.post("/api/auth/register", json={
        "email": "elder_a@example.com",
        "password": "Password123!",
        "name": "Elder Alice",
        "role": "ELDER",
    })
    token_a = reg_a.get_json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 1. Create Caregiver
    create_payload = {
        "name": "Son Bob",
        "phone": "+919876500001",
        "email": "bob@example.com",
        "relationship": "SON",
        "notification_preferences": {
            "sms_enabled": True,
            "voice_enabled": True,
            "high_risk_enabled": True,
        },
    }
    create_res = client.post("/api/caregivers", json=create_payload, headers=headers_a)
    assert create_res.status_code == 201
    cg = create_res.get_json()
    cg_id = cg["caregiver_id"]
    assert cg["status"] == "PENDING"
    assert cg["is_verified"] is False
    assert cg["relationship"] == "SON"

    # 2. List Caregivers
    list_res = client.get("/api/caregivers", headers=headers_a)
    assert list_res.status_code == 200
    items = list_res.get_json()
    assert any(item["caregiver_id"] == cg_id for item in items)

    # 3. Get Single Caregiver
    get_res = client.get(f"/api/caregivers/{cg_id}", headers=headers_a)
    assert get_res.status_code == 200
    assert get_res.get_json()["name"] == "Son Bob"

    # 4. Verify Caregiver
    verify_res = client.post(f"/api/caregivers/{cg_id}/verify", headers=headers_a)
    assert verify_res.status_code == 200
    assert verify_res.get_json()["is_verified"] is True
    assert verify_res.get_json()["status"] == "VERIFIED"

    # 5. Patch Notification Preferences
    patch_payload = {
        "notification_preferences": {
            "voice_enabled": False,
            "max_notifications_per_hour": 3,
        }
    }
    patch_res = client.patch(f"/api/caregivers/{cg_id}", json=patch_payload, headers=headers_a)
    assert patch_res.status_code == 200
    updated_prefs = patch_res.get_json()["notification_preferences"]
    assert updated_prefs["voice_enabled"] is False
    assert updated_prefs["max_notifications_per_hour"] == 3

    # 6. Delete (Deactivate) Caregiver
    del_res = client.delete(f"/api/caregivers/{cg_id}", headers=headers_a)
    assert del_res.status_code == 200

    # Verify no longer active in active list
    list_after = client.get("/api/caregivers", headers=headers_a).get_json()
    assert not any(item["caregiver_id"] == cg_id for item in list_after)


def test_11_caregiver_ownership_isolation(client):
    """Elder B cannot view or modify Elder A's caregivers (Ownership check)."""
    # Login Elder A
    reg_a = client.post("/api/auth/register", json={
        "email": "elder_owner@example.com",
        "password": "Password123!",
        "name": "Elder Owner",
    })
    token_a = reg_a.get_json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register Elder B
    reg_b = client.post("/api/auth/register", json={
        "email": "elder_intruder@example.com",
        "password": "Password123!",
        "name": "Elder Intruder",
    })
    token_b = reg_b.get_json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Elder A creates caregiver
    cg_res = client.post("/api/caregivers", json={
        "name": "Trusted Daughter",
        "phone": "+919876544444",
        "email": "daughter@example.com",
        "relationship": "DAUGHTER",
    }, headers=headers_a)
    cg_id = cg_res.get_json()["caregiver_id"]

    # Elder B attempts to GET Elder A's caregiver -> 403 Forbidden
    get_res = client.get(f"/api/caregivers/{cg_id}", headers=headers_b)
    assert get_res.status_code == 403

    # Elder B attempts to PATCH Elder A's caregiver -> 403 Forbidden
    patch_res = client.patch(f"/api/caregivers/{cg_id}", json={"name": "Hacked"}, headers=headers_b)
    assert patch_res.status_code == 403

    # Elder B attempts to DELETE Elder A's caregiver -> 403 Forbidden
    del_res = client.delete(f"/api/caregivers/{cg_id}", headers=headers_b)
    assert del_res.status_code == 403


# =====================================================================
# 3. NOTIFICATION & TWILIO MOCK TESTS
# =====================================================================

def test_12_mock_twilio_service():
    """Mock Twilio client simulates SMS and Voice without network calls."""
    mock_client = get_mock_twilio_client()
    mock_client.sent_messages.clear()
    mock_client.made_calls.clear()

    # Send SMS
    sms_res = mock_client.send_sms("+919876543210", "Test Alert Message")
    assert sms_res["status"] == "SENT"
    assert sms_res["sid"].startswith("SM_MOCK_")
    assert len(mock_client.sent_messages) == 1

    # Make Voice Call
    call_res = mock_client.make_call("+919876543210", "<Response><Say>Hello</Say></Response>")
    assert call_res["status"] == "SENT"
    assert call_res["sid"].startswith("CA_MOCK_")
    assert len(mock_client.made_calls) == 1


def test_13_message_builder_safety_and_privacy():
    """Message builder adheres to strict safety rules and masks private info."""
    # Masking
    assert mask_phone_number("+919876543210") == "+91***210"
    assert mask_recipient("rajesh.kumar@okhdfcbank") == "ra***r@okhdfcbank"

    # SMS Advisory Text
    sms = build_caregiver_sms_text(
        elder_name="Sunita Sharma",
        risk_level="CRITICAL",
        risk_score=92,
        amount=50000,
        recipient="fraudster@upi",
        reason="Suspicious communication followed by unusual velocity",
    )
    # MUST contain safe advisory wording
    assert "automated risk alert, not a confirmed fraud determination" in sms
    assert "Critical-risk activity detected" in sms
    # MUST NOT claim confirmed fraud
    assert "fraud confirmed" not in sms.lower()
    assert "account compromised" not in sms.lower()

    # Voice Advisory TwiML
    twiml = build_caregiver_voice_twiml("Sunita Sharma", "CRITICAL")
    assert "<Response>" in twiml
    assert "automated risk warning and not a confirmed fraud determination" in twiml
    assert "Polly.Aditi" in twiml


def test_14_escalation_low_and_medium_no_notification():
    """LOW and MEDIUM risk levels do NOT trigger caregiver alerts."""
    low_event = {
        "final_risk_score": 15,
        "risk_level": "LOW",
        "transaction_id": "TXN_LOW_01",
    }
    res_low = EscalationService.escalate_risk_event(low_event, user_id="usr_elder_low")
    assert res_low["triggered"] is False
    assert res_low["reason"] == "LOW_RISK_NO_NOTIFICATION"

    med_event = {
        "final_risk_score": 50,
        "risk_level": "MEDIUM",
        "transaction_id": "TXN_MED_01",
    }
    res_med = EscalationService.escalate_risk_event(med_event, user_id="usr_elder_med")
    assert res_med["triggered"] is False
    assert res_med["reason"] == "MEDIUM_RISK_NO_NOTIFICATION"


def test_15_escalation_high_and_critical_triggers_mock(client):
    """HIGH risk triggers SMS and CRITICAL triggers SMS + Voice to verified caregiver."""
    mock_client = get_mock_twilio_client()
    mock_client.sent_messages.clear()
    mock_client.made_calls.clear()

    # Create elder
    reg = client.post("/api/auth/register", json={
        "email": "elder_escalation@example.com",
        "password": "Password123!",
        "name": "Elder Esc",
    })
    elder = reg.get_json()["user"]
    elder_id = elder["user_id"]
    headers = {"Authorization": f"Bearer {reg.get_json()['access_token']}"}

    # Add verified caregiver with voice enabled
    cg_res = client.post("/api/caregivers", json={
        "name": "Caregiver Esc",
        "phone": "+919876599999",
        "email": "cgesc@example.com",
        "relationship": "DAUGHTER",
        "notification_preferences": {
            "sms_enabled": True,
            "voice_enabled": True,
            "high_risk_enabled": True,
            "critical_risk_enabled": True,
        },
    }, headers=headers)
    cg_id = cg_res.get_json()["caregiver_id"]
    client.post(f"/api/caregivers/{cg_id}/verify", headers=headers)

    # Trigger HIGH risk event
    high_event = {
        "risk_event_id": "evt_high_001",
        "transaction_id": "TXN_HIGH_01",
        "final_risk_score": 75,
        "risk_level": "HIGH",
        "features_analyzed": {
            "transaction_features": {"amount": 25000, "recipient": "merchant@icici"}
        },
        "contributing_factors": ["Unusual late night transaction."],
    }
    res_high = EscalationService.escalate_risk_event(high_event, user_id=elder_id)
    assert res_high["triggered"] is True
    assert res_high["caregivers_notified_count"] >= 1
    assert len(mock_client.sent_messages) >= 1

    # Trigger CRITICAL risk event
    crit_event = {
        "risk_event_id": "evt_crit_001",
        "transaction_id": "TXN_CRIT_01",
        "final_risk_score": 95,
        "risk_level": "CRITICAL",
        "features_analyzed": {
            "transaction_features": {"amount": 90000, "recipient": "scammer@paytm"}
        },
        "contributing_factors": ["Immediate transaction following KYC scam call."],
    }
    res_crit = EscalationService.escalate_risk_event(crit_event, user_id=elder_id)
    assert res_crit["triggered"] is True
    # SMS + Voice should both be called
    assert len(mock_client.made_calls) >= 1


def test_16_notification_deduplication(client):
    """Subsequent calls for the same risk event ID do NOT duplicate notifications."""
    reg = client.post("/api/auth/register", json={
        "email": "elder_dedup@example.com",
        "password": "Password123!",
        "name": "Elder Dedup",
    })
    elder_id = reg.get_json()["user"]["user_id"]
    headers = {"Authorization": f"Bearer {reg.get_json()['access_token']}"}

    cg_res = client.post("/api/caregivers", json={
        "name": "Caregiver Dedup",
        "phone": "+919876588888",
        "email": "dedup_cg@example.com",
    }, headers=headers)
    cg_id = cg_res.get_json()["caregiver_id"]
    client.post(f"/api/caregivers/{cg_id}/verify", headers=headers)

    mock_client = get_mock_twilio_client()
    mock_client.sent_messages.clear()

    event = {
        "risk_event_id": "evt_idempotent_100",
        "transaction_id": "TXN_DEDUP_01",
        "final_risk_score": 85,
        "risk_level": "HIGH",
    }

    # First dispatch
    res1 = EscalationService.escalate_risk_event(event, user_id=elder_id)
    assert res1["caregivers_notified_count"] == 1
    count_after_first = len(mock_client.sent_messages)

    # Second dispatch with identical event
    res2 = EscalationService.escalate_risk_event(event, user_id=elder_id)
    assert res2["caregivers_notified_count"] == 0
    # No extra message sent
    assert len(mock_client.sent_messages) == count_after_first


def test_17_caregiver_acknowledgement(client):
    """Caregiver or elder acknowledges a risk notification."""
    reg = client.post("/api/auth/register", json={
        "email": "elder_ack@example.com",
        "password": "Password123!",
        "name": "Elder Ack",
    })
    elder_id = reg.get_json()["user"]["user_id"]
    headers = {"Authorization": f"Bearer {reg.get_json()['access_token']}"}

    cg_res = client.post("/api/caregivers", json={
        "name": "Caregiver Ack",
        "phone": "+919876577777",
        "email": "ack_cg@example.com",
    }, headers=headers)
    cg_id = cg_res.get_json()["caregiver_id"]
    client.post(f"/api/caregivers/{cg_id}/verify", headers=headers)

    # Trigger escalation
    escalation_res = EscalationService.escalate_risk_event({
        "risk_event_id": "evt_ack_001",
        "final_risk_score": 88,
        "risk_level": "HIGH",
    }, user_id=elder_id)

    dispatched = escalation_res["dispatched"]
    assert len(dispatched) > 0
    notif_id = dispatched[0]["notification_id"]

    # Acknowledge via API
    ack_res = client.post(f"/api/notifications/{notif_id}/acknowledge", headers=headers)
    assert ack_res.status_code == 200
    ack_data = ack_res.get_json()
    assert ack_data["is_acknowledged"] is True
    assert ack_data["acknowledged_by"] == elder_id
    assert ack_data["acknowledged_at"] is not None


def test_18_quiet_hours_utility():
    """Quiet hours calculation handles daytime and midnight crossing correctly."""
    from datetime import datetime
    # Window: 22:00 to 07:00
    night_time = datetime(2026, 10, 8, 23, 30)
    day_time = datetime(2026, 10, 8, 14, 0)
    early_morning = datetime(2026, 10, 8, 5, 0)

    assert is_in_quiet_hours("22:00", "07:00", night_time) is True
    assert is_in_quiet_hours("22:00", "07:00", early_morning) is True
    assert is_in_quiet_hours("22:00", "07:00", day_time) is False
