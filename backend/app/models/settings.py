"""UPI Guardian - Settings Model and Store."""

USER_SETTINGS: dict = {
    "profile": {
        "name": "Sunita Devi",
        "age": 68,
        "phone": "+91 ••••• ••410",
        "email": "sunita.demo@example.com",
    },
    "security": {
        "twoFactor": True,
        "loginActivityAlerts": True,
    },
    "alertPreferences": {
        "highRiskTransactions": True,
        "scamCalls": True,
        "scamSms": True,
        "familyNotifications": True,
    },
    "accessibility": {
        "seniorMode": False,
        "highContrast": False,
        "reducedMotion": False,
        "voiceAssistance": False,
    },
}


def get_user_settings() -> dict:
    """Retrieve user settings."""
    return dict(USER_SETTINGS)


def update_user_settings(updates: dict) -> dict:
    """Partially update user settings."""
    for section, values in updates.items():
        if section in USER_SETTINGS and isinstance(values, dict):
            USER_SETTINGS[section].update(values)
        elif section in USER_SETTINGS:
            USER_SETTINGS[section] = values
    return dict(USER_SETTINGS)
