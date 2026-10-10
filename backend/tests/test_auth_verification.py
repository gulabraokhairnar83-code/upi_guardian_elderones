"""UPI Guardian - Complete Authentication Verification Test Suite.

Tests:
1. User registration (Elder & Caregiver roles)
2. Duplicate registration conflict rejection
3. Successful login & JWT issuance
4. Invalid password rejection (401)
5. Non-existent email rejection (401)
6. Protected route (/api/auth/me) access with and without Bearer JWT
7. Logout and token revocation enforcement
8. Forgot password endpoint validation and submission
9. Default seeded demo accounts login verification
"""

import pytest
from app import create_app
from app.db.connection import get_db


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as test_client:
        yield test_client


def test_seed_demo_accounts_login(client):
    """Test that pre-seeded demo accounts can authenticate immediately."""
    # Test Sunita Devi (Elder)
    res_sunita = client.post(
        "/api/auth/login",
        json={"email": "sunita.demo@example.com", "password": "GuardianPass123!"},
    )
    assert res_sunita.status_code == 200
    data_sunita = res_sunita.get_json()
    assert data_sunita["success"] is True
    assert data_sunita["user"]["name"] == "Sunita Devi"
    assert data_sunita["user"]["role"] == "ELDER"
    assert "access_token" in data_sunita
    assert "password_hash" not in data_sunita["user"]

    # Test Rohit Caregiver
    res_rohit = client.post(
        "/api/auth/login",
        json={"email": "rohit.caregiver@example.com", "password": "GuardianPass123!"},
    )
    assert res_rohit.status_code == 200
    data_rohit = res_rohit.get_json()
    assert data_rohit["success"] is True
    assert data_rohit["user"]["name"] == "Rohit Caregiver"
    assert data_rohit["user"]["role"] == "CAREGIVER"


def test_registration_flow(client):
    """Test complete user registration for both Elder and Caregiver roles."""
    elder_payload = {
        "name": "Kishore Kumar",
        "email": "kishore.test@example.com",
        "password": "SecurePassword123!",
        "role": "ELDER",
        "phone": "+91 99887 76655",
    }
    res_elder = client.post("/api/auth/register", json=elder_payload)
    assert res_elder.status_code == 201
    data_elder = res_elder.get_json()
    assert data_elder["success"] is True
    assert data_elder["user"]["email"] == "kishore.test@example.com"
    assert data_elder["user"]["role"] == "ELDER"
    assert "access_token" in data_elder
    assert "refresh_token" in data_elder

    # Caregiver registration
    caregiver_payload = {
        "name": "Ananya Sharma",
        "email": "ananya.care@example.com",
        "password": "SecurePassword123!",
        "role": "CAREGIVER",
    }
    res_cg = client.post("/api/auth/register", json=caregiver_payload)
    assert res_cg.status_code == 201
    assert res_cg.get_json()["user"]["role"] == "CAREGIVER"


def test_registration_duplicate_email_conflict(client):
    """Test that registering with an already existing email returns 409 Conflict."""
    payload = {
        "name": "Duplicate User",
        "email": "sunita.demo@example.com",
        "password": "Password123!",
        "role": "ELDER",
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 409
    data = res.get_json()
    assert "already exists" in data.get("error", "").lower()


def test_login_invalid_password(client):
    """Test that login with incorrect password returns 401 Unauthorized."""
    res = client.post(
        "/api/auth/login",
        json={"email": "sunita.demo@example.com", "password": "WrongPassword999!"},
    )
    assert res.status_code == 401
    data = res.get_json()
    assert "invalid email or password" in data.get("error", "").lower()


def test_login_nonexistent_email(client):
    """Test that login with unknown email returns 401 Unauthorized."""
    res = client.post(
        "/api/auth/login",
        json={"email": "nobody.unknown@example.com", "password": "SomePassword123!"},
    )
    assert res.status_code == 401


def test_protected_route_access(client):
    """Test accessing protected endpoint /api/auth/me with and without valid token."""
    # 1. Unauthenticated request without token must fail
    res_unauth = client.get("/api/auth/me")
    assert res_unauth.status_code == 401
    assert "missing authentication token" in res_unauth.get_json().get("error", "").lower()

    # 2. Malformed token must fail
    res_bad_token = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer this-is-a-garbage-token"},
    )
    assert res_bad_token.status_code == 401

    # 3. Authenticated request with valid token succeeds
    login_res = client.post(
        "/api/auth/login",
        json={"email": "sunita.demo@example.com", "password": "GuardianPass123!"},
    )
    token = login_res.get_json()["access_token"]

    res_auth = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_auth.status_code == 200
    user_me = res_auth.get_json()["user"]
    assert user_me["email"] == "sunita.demo@example.com"
    assert "password_hash" not in user_me


def test_logout_and_revocation(client):
    """Test logging out revokes the access token and subsequent requests are rejected."""
    # Log in
    login_res = client.post(
        "/api/auth/login",
        json={"email": "sunita.demo@example.com", "password": "GuardianPass123!"},
    )
    token = login_res.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify access before logout
    check_before = client.get("/api/auth/me", headers=headers)
    assert check_before.status_code == 200

    # Logout
    logout_res = client.post("/api/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.get_json()["success"] is True

    # Attempting to use the revoked token must fail with 401
    check_after = client.get("/api/auth/me", headers=headers)
    assert check_after.status_code == 401
    assert "revoked" in check_after.get_json().get("error", "").lower()


def test_forgot_password_flow(client):
    """Test POST /api/auth/forgot-password handles valid and invalid requests."""
    # Valid email
    res_valid = client.post(
        "/api/auth/forgot-password",
        json={"email": "sunita.demo@example.com"},
    )
    assert res_valid.status_code == 200
    data_valid = res_valid.get_json()
    assert data_valid["success"] is True
    assert "dispatched" in data_valid["message"].lower()

    # Invalid email format
    res_invalid = client.post(
        "/api/auth/forgot-password",
        json={"email": "not-an-email"},
    )
    assert res_invalid.status_code == 400

    # Missing email
    res_missing = client.post(
        "/api/auth/forgot-password",
        json={},
    )
    assert res_missing.status_code == 400
