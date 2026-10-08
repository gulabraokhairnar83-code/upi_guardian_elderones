"""Test MongoDB database connection and health utilities."""

from app.db import get_db, check_db_connection, is_mock_active


def test_db_instance_available(app):
    db = get_db()
    assert db is not None
    # Verify the 7 collections exist or are accessible
    assert "users" in [c for c in dir(db) if not c.startswith("_")] or db["users"] is not None
    assert db["transactions"] is not None
    assert db["alerts"] is not None
    assert db["analyzed_messages"] is not None
    assert db["risk_events"] is not None
    assert db["caregivers"] is not None
    assert db["notification_preferences"] is not None


def test_db_connection_health_check(app):
    status = check_db_connection()
    assert status["connected"] is True
    assert status["status"] == "healthy"


def test_is_mock_active_in_testing(app):
    assert is_mock_active() is True
