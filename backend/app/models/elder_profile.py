"""UPI Guardian - Elder Profile & Family Data Model."""

ELDER_PROFILE: dict = {
    "id": "elder-sunita-01",
    "name": "Sunita Devi",
    "age": 68,
    "location": "Pune",
    "accountSafetyStatus": "Protected",
    "phone": "+91 ••••• ••410",
    "email": "sunita.demo@example.com",
    "twoFactorEnabled": True,
    "loginAlertsEnabled": True,
    "metrics": {
        "currentRiskScore": 27,
        "todayTransactionsCount": 8,
        "activeAlertsCount": 2,
        "scamCommunicationsCount": 3,
    },
}


def get_elder_profile() -> dict:
    """Retrieve elder family profile."""
    return dict(ELDER_PROFILE)


def resolve_family_alerts() -> dict:
    """Mark active family alerts resolved."""
    ELDER_PROFILE["metrics"]["activeAlertsCount"] = 0
    return dict(ELDER_PROFILE)
