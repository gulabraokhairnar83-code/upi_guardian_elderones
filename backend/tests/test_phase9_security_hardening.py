"""UPI Guardian - Phase 9 Security Hardening & Regression Test Suite.

Verifies:
- JWT expiration, signature verification, malformed token, and revocation handling
- Password validation and generic auth responses (no user enumeration)
- Inactive user access restrictions
- Role-based authorization enforcement
- Token misuse prevention (refresh vs access separation)
- Rate limiting protection on sensitive endpoints
- HTTP Security Headers compliance
- Twilio delivery receipt webhook safety and validation
- Sanitized error handling and prevention of stack trace / credential leaks
"""

import time
import pytest
import jwt
from datetime import datetime, timezone, timedelta
from app import create_app
from app.utils.auth import (
    create_access_token,
    create_refresh_token,
    revoke_token,
    get_jwt_secret,
)
from app.db.repositories.user_repository import UserRepository
from app.notifications.notification_repository import NotificationRepository
from app.utils.rate_limiter import reset_rate_limiter


@pytest.fixture
def app():
    """Create test application instance with testing configuration."""
    test_app = create_app("testing")
    test_app.config["TESTING"] = True
    test_app.config["RATE_LIMIT_ENABLED"] = True
    yield test_app


@pytest.fixture
def client(app):
    """Flask test client."""
    reset_rate_limiter()
    return app.test_client()


class TestJWTSecurityHardening:
    """JWT authentication and authorization security verification."""

    def test_missing_authorization_header(self, client):
        """Protected endpoints reject requests missing the Authorization header with 401."""
        res = client.get("/api/auth/me")
        assert res.status_code == 401
        data = res.get_json()
        assert "error" in data
        assert "token" in data["error"].lower() or "missing" in data["error"].lower()

    def test_malformed_token_returns_401(self, client):
        """Malformed or corrupt Bearer tokens return safe 401."""
        headers = {"Authorization": "Bearer not.a.valid.jwt.token"}
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 401
        data = res.get_json()
        assert "error" in data

    def test_invalid_signature_token_returns_401(self, client):
        """Tokens signed with a different secret return 401."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "usr_fake_attacker",
            "user_id": "usr_fake_attacker",
            "role": "ELDER",
            "email": "attacker@example.com",
            "jti": "fake_jti_123",
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
        }
        bogus_token = jwt.encode(payload, "unauthorized-different-secret-key", algorithm="HS256")
        headers = {"Authorization": f"Bearer {bogus_token}"}
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 401
        assert "Invalid" in res.get_json()["error"]

    def test_expired_access_token_returns_401(self, client, app):
        """Expired access tokens return 401 with informative expired message."""
        with app.app_context():
            expired_token = create_access_token(
                user_id="usr_sunita_68",
                role="ELDER",
                email="sunita@example.com",
                expires_in_seconds=-60,  # Expired 60 seconds ago
            )
        headers = {"Authorization": f"Bearer {expired_token}"}
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 401
        assert "expired" in res.get_json()["error"].lower()

    def test_revoked_token_returns_401(self, client, app):
        """Revoked tokens cannot access protected endpoints."""
        with app.app_context():
            token = create_access_token(
                user_id="usr_sunita_68",
                role="ELDER",
                email="sunita@example.com",
            )
            decoded = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
            revoke_token(decoded["jti"], decoded["exp"])

        headers = {"Authorization": f"Bearer {token}"}
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 401
        assert "revoked" in res.get_json()["error"].lower()

    def test_refresh_token_misuse_as_access_token(self, client, app):
        """Using a refresh token on an access-token protected endpoint returns 401."""
        with app.app_context():
            refresh_tok = create_refresh_token(user_id="usr_sunita_68")

        headers = {"Authorization": f"Bearer {refresh_tok}"}
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 401
        assert "access token expected" in res.get_json()["error"].lower()

    def test_access_token_misuse_as_refresh_token(self, client, app):
        """Using an access token on the /api/auth/refresh endpoint returns 401."""
        with app.app_context():
            access_tok = create_access_token(
                user_id="usr_sunita_68",
                role="ELDER",
                email="sunita@example.com",
            )

        res = client.post("/api/auth/refresh", json={"refresh_token": access_tok})
        assert res.status_code == 401
        assert "refresh token expected" in res.get_json()["error"].lower()

    def test_inactive_user_token_access_rejected(self, client, app):
        """Tokens belonging to deactivated accounts return 401."""
        repo = UserRepository()
        user_id = f"usr_deactivated_{int(time.time())}"
        repo.create_user({
            "user_id": user_id,
            "name": "Deactivated User",
            "email": f"deact_{int(time.time())}@example.com",
            "password_hash": "scrypt:dummy",
            "role": "ELDER",
            "is_active": False,
        })

        with app.app_context():
            token = create_access_token(
                user_id=user_id,
                role="ELDER",
                email=f"deact_{int(time.time())}@example.com",
            )

        headers = {"Authorization": f"Bearer {token}"}
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 401
        assert "deactivated" in res.get_json()["error"].lower()

    def test_wrong_role_returns_403(self, client, app):
        """Users with unauthorized role receive 403 Forbidden on role-restricted endpoints."""
        with app.app_context():
            elder_token = create_access_token(
                user_id="usr_elder_only",
                role="ELDER",
                email="elder@example.com",
            )

        # /api/caregivers endpoint requires CAREGIVER role to list all elders or perform caregiver management
        # Test acknowledging without permission
        headers = {"Authorization": f"Bearer {elder_token}"}
        # Attempt acknowledge a notification not belonging to this user
        notif_repo = NotificationRepository()
        notif = notif_repo.create_notification({
            "notification_id": f"notif_foreign_{int(time.time())}",
            "user_id": "usr_other_elder",
            "caregiver_id": "cg_other_caregiver",
            "channel": "SMS",
            "status": "SENT",
        })

        res = client.post(f"/api/notifications/{notif['notification_id']}/acknowledge", headers=headers)
        assert res.status_code == 403
        assert "not authorized" in res.get_json()["error"].lower()


class TestPasswordAndAuthSecurity:
    """Password hashing, registration validation, and enumeration defense."""

    def test_weak_password_rejected(self, client):
        """Passwords under 8 chars or missing numbers/letters are rejected with 400."""
        # Short password
        res = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "testshort@example.com",
                "password": "short",
            },
        )
        assert res.status_code == 400
        assert "at least 8 characters" in res.get_json()["error"].lower()

        # No numbers
        res = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "testnonum@example.com",
                "password": "onlylettershere",
            },
        )
        assert res.status_code == 400
        assert "letter and one number" in res.get_json()["error"].lower()

    def test_duplicate_email_registration_prevented(self, client):
        """Registering with an already existing email returns 409 Conflict."""
        email = f"duplicate_{int(time.time())}@example.com"
        payload = {
            "name": "First Account",
            "email": email,
            "password": "SecurePassword123",
            "role": "ELDER",
        }
        res1 = client.post("/api/auth/register", json=payload)
        assert res1.status_code == 201

        res2 = client.post("/api/auth/register", json=payload)
        assert res2.status_code == 409
        assert "already exists" in res2.get_json()["error"].lower()

    def test_login_invalid_credentials_prevents_email_enumeration(self, client):
        """Failed logins return generic 'Invalid email or password' preventing email enumeration."""
        # Non-existent email
        res1 = client.post(
            "/api/auth/login",
            json={"email": "nonexistent_email_12345@example.com", "password": "WrongPassword123"},
        )
        assert res1.status_code == 401
        assert res1.get_json()["error"] == "Invalid email or password."

        # Existing user with wrong password
        res2 = client.post(
            "/api/auth/login",
            json={"email": "sunita@example.com", "password": "WrongPassword123"},
        )
        assert res2.status_code == 401
        assert res2.get_json()["error"] == "Invalid email or password."

    def test_password_hash_never_returned_in_api_responses(self, client):
        """Password hashes are stripped from register, login, and me endpoints."""
        email = f"hashleak_{int(time.time())}@example.com"
        reg_res = client.post(
            "/api/auth/register",
            json={
                "name": "Hash Test User",
                "email": email,
                "password": "SecurePassword123",
                "role": "ELDER",
            },
        )
        assert reg_res.status_code == 201
        reg_data = reg_res.get_json()
        assert "password_hash" not in reg_data.get("user", {})
        assert "password" not in reg_data.get("user", {})

        # Login
        login_res = client.post(
            "/api/auth/login",
            json={"email": email, "password": "SecurePassword123"},
        )
        assert login_res.status_code == 200
        login_data = login_res.get_json()
        assert "password_hash" not in login_data.get("user", {})
        assert "password" not in login_data.get("user", {})

        # Get me
        token = login_data["access_token"]
        me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert "password_hash" not in me_res.get_json().get("user", {})

    def test_inactive_account_login_rejected(self, client):
        """Deactivated accounts cannot authenticate via login."""
        repo = UserRepository()
        email = f"inactive_login_{int(time.time())}@example.com"
        from app.utils.auth import hash_password
        repo.create_user({
            "user_id": f"usr_inact_{int(time.time())}",
            "name": "Deactivated User",
            "email": email,
            "password_hash": hash_password("ValidPassword123"),
            "role": "ELDER",
            "is_active": False,
        })

        res = client.post(
            "/api/auth/login",
            json={"email": email, "password": "ValidPassword123"},
        )
        assert res.status_code == 401
        assert res.get_json()["error"] == "Invalid email or password."


class TestSecurityHeadersAndCORS:
    """Security headers and cross-origin security."""

    def test_security_headers_present(self, client):
        """All responses include essential HTTP security headers."""
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.headers.get("X-Content-Type-Options") == "nosniff"
        assert res.headers.get("X-Frame-Options") == "DENY"
        assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert "geolocation=()" in res.headers.get("Permissions-Policy", "")
        assert "default-src 'self'" in res.headers.get("Content-Security-Policy", "")

    def test_health_check_does_not_leak_secrets(self, client):
        """Health check returns clean status without database credentials."""
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "healthy"
        assert "mongodb+srv" not in str(data)
        assert "password" not in str(data)
        assert "secret" not in str(data).lower()


class TestRateLimitingAndWebhook:
    """Rate limiter enforcement and delivery receipt webhook validation."""

    def test_auth_login_rate_limit(self, client):
        """Rapid repeated requests exceed rate limit and return 429 Too Many Requests."""
        reset_rate_limiter()
        # Rate limit on login is 15 requests per minute
        responses = []
        for i in range(17):
            res = client.post(
                "/api/auth/login",
                json={"email": f"rate_{i}@example.com", "password": "Password123"},
            )
            responses.append(res.status_code)

        assert 429 in responses
        assert responses[-1] == 429

    def test_webhook_valid_delivery_receipt(self, client, app):
        """POST /api/notifications/webhook updates notification status safely."""
        with app.app_context():
            notif_repo = NotificationRepository()
            provider_sid = f"SM_TEST_{int(time.time())}"
            notif = notif_repo.create_notification({
                "notification_id": f"notif_wbk_{int(time.time())}",
                "user_id": "usr_sunita_68",
                "caregiver_id": "cg_son_rohit",
                "channel": "SMS",
                "status": "SENT",
                "provider_message_id": provider_sid,
            })

        # Send delivery status callback
        res = client.post(
            "/api/notifications/webhook",
            json={
                "MessageSid": provider_sid,
                "MessageStatus": "delivered",
            },
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["status"] == "delivered"
        assert data["updated"] is True

        # Verify DB updated
        with app.app_context():
            updated = notif_repo.get_by_id(notif["notification_id"])
            assert updated["status"] == "DELIVERED"
            assert updated["delivered_at"] is not None

    def test_webhook_malformed_payload_rejected(self, client):
        """Webhook with missing SID or status returns 400."""
        res1 = client.post("/api/notifications/webhook", json={})
        assert res1.status_code == 400

        res2 = client.post("/api/notifications/webhook", json={"MessageSid": "SM_123"})
        assert res2.status_code == 400

    def test_input_validation_boundaries(self, client):
        """Enormous amounts and strings are safely rejected with 400."""
        # Oversized amount (> 1 Crore)
        res1 = client.post(
            "/api/analyze-transaction",
            json={
                "payee": "Merchant",
                "amount": 99999999999,
                "upiId": "merchant@upi",
            },
        )
        assert res1.status_code == 400
        assert "exceeds maximum permitted" in res1.get_json()["error"]

        # Oversized message (> 5000 chars)
        res2 = client.post(
            "/api/analyze-message",
            json={
                "text": "A" * 6000,
                "message_type": "sms",
            },
        )
        assert res2.status_code == 400
        assert "exceeds maximum allowed length" in res2.get_json()["error"]
