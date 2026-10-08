"""UPI Guardian - Notification & Settings Repository."""

from datetime import datetime, timezone
from app.db.repositories.base_repository import BaseRepository
from app.db.seed_data import PRIMARY_USER_ID


class SettingsRepository(BaseRepository):
    """Data access layer for notification_preferences collection."""

    def __init__(self):
        super().__init__("notification_preferences")

    def get_settings(self, user_id: str = PRIMARY_USER_ID) -> dict:
        doc = self.collection.find_one({"user_id": user_id})
        cleaned = self.clean_doc(doc)
        if not cleaned:
            return {
                "profile": {
                    "name": "Sunita Devi",
                    "age": 68,
                    "phone": "+91 ••••• ••410",
                    "email": "sunita.demo@example.com",
                },
                "security": {"twoFactor": True, "loginActivityAlerts": True},
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

        return {
            "profile": cleaned.get("profile", {}),
            "security": cleaned.get("security", {}),
            "alertPreferences": cleaned.get("alertPreferences", {}),
            "accessibility": cleaned.get("accessibility", {}),
        }

    def update_settings(self, updates: dict, user_id: str = PRIMARY_USER_ID) -> dict:
        set_payload = {}
        for section, values in updates.items():
            if isinstance(values, dict):
                for sub_key, sub_val in values.items():
                    set_payload[f"{section}.{sub_key}"] = sub_val
            else:
                set_payload[section] = values

        set_payload["updated_at"] = datetime.now(timezone.utc).isoformat()

        self.collection.update_one(
            {"user_id": user_id},
            {"$set": set_payload},
            upsert=True,
        )
        return self.get_settings(user_id)
