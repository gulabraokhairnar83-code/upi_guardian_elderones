"""Test MongoDB repository layer and CRUD operations."""

from app.db.repositories.transaction_repository import TransactionRepository
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.family_repository import FamilyRepository
from app.db.repositories.settings_repository import SettingsRepository
from app.db.repositories.message_repository import MessageRepository


def test_transaction_repository_crud(app):
    repo = TransactionRepository()
    all_tx = repo.list_transactions()
    assert len(all_tx) >= 24

    # Test get_by_id
    tx = repo.get_by_id("TXN-UG-928401")
    assert tx is not None
    assert tx["id"] == "TXN-UG-928401"
    assert "payee" in tx
    assert "amount" in tx
    assert "user_id" in tx
    assert "transaction_type" in tx
    assert "historical_average" in tx

    # Test filtering
    critical_tx = repo.list_transactions(status="critical")
    assert all(t["status"] == "critical" for t in critical_tx)

    # Test count
    count = repo.count()
    assert count >= 24


def test_alert_repository_crud(app):
    repo = AlertRepository()
    alerts = repo.list_alerts()
    assert len(alerts) >= 3

    # Test resolve
    res = repo.resolve_alert(1)
    assert res is not None
    assert res["status"] == "resolved"


def test_family_repository_crud(app):
    repo = FamilyRepository()
    profile = repo.get_elder_profile()
    assert profile is not None
    assert profile["name"] == "Sunita Devi"
    assert "metrics" in profile

    caregivers = repo.get_caregivers()
    assert len(caregivers) >= 3
    assert any(c["relation"] == "Son" for c in caregivers)


def test_settings_repository_crud(app):
    repo = SettingsRepository()
    settings = repo.get_settings()
    assert "profile" in settings
    assert "accessibility" in settings

    # Update
    updated = repo.update_settings({"accessibility": {"seniorMode": True}})
    assert updated["accessibility"]["seniorMode"] is True


def test_message_repository_crud(app):
    repo = MessageRepository()
    saved = repo.save_analysis(
        {"text": "OTP test message", "type": "sms"},
        {"riskScore": 85, "level": "high", "isSuspicious": True},
    )
    assert saved is not None
    assert saved["text"] == "OTP test message"
    assert saved["risk_score"] == 85
    assert saved["is_synthetic"] is True
