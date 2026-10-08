"""UPI Guardian - Notifications Configuration."""

import os
from flask import current_app


def get_twilio_config() -> dict:
    """Retrieve Twilio settings securely from current application config or environment."""
    if current_app:
        enabled = current_app.config.get("TWILIO_ENABLED", False)
        account_sid = current_app.config.get("TWILIO_ACCOUNT_SID", "")
        auth_token = current_app.config.get("TWILIO_AUTH_TOKEN", "")
        from_phone = current_app.config.get("TWILIO_FROM_PHONE", "")
    else:
        enabled = os.environ.get("TWILIO_ENABLED", "false").lower() in ("true", "1", "yes")
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        from_phone = os.environ.get("TWILIO_FROM_PHONE", "")

    return {
        "enabled": bool(enabled and account_sid and auth_token and from_phone),
        "raw_enabled": bool(enabled),
        "account_sid": account_sid,
        "auth_token": auth_token,
        "from_phone": from_phone,
    }


DEFAULT_MAX_NOTIFICATIONS_PER_HOUR = 5
DEFAULT_QUIET_HOURS_START = "22:00"
DEFAULT_QUIET_HOURS_END = "07:00"
