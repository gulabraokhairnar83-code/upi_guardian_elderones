"""UPI Guardian - Caregiver Repository."""

from datetime import datetime, timezone
import re
from app.db.repositories.base_repository import BaseRepository
from app.db.seed_data import PRIMARY_USER_ID


class CaregiverRepository(BaseRepository):
    """Data access layer for caregivers collection."""

    def __init__(self):
        super().__init__("caregivers")

    def list_caregivers(self, elder_user_id: str, is_active: bool | None = True) -> list[dict]:
        """List caregivers associated with a specific elder user."""
        query: dict = {
            "$or": [
                {"elder_user_id": elder_user_id},
                {"user_id": elder_user_id},  # backward compatibility with seed data
            ]
        }
        if is_active is not None:
            query["is_active"] = is_active

        cursor = self.collection.find(query).sort("created_at", -1)
        return self.clean_docs(list(cursor))

    def get_by_id(self, caregiver_id: str) -> dict | None:
        """Find caregiver record by caregiver_id."""
        pattern = {"$regex": f"^{re.escape(caregiver_id.strip())}$", "$options": "i"}
        doc = self.collection.find_one({"caregiver_id": pattern})
        return self.clean_doc(doc)

    def create_caregiver(self, data: dict) -> dict:
        """Create new caregiver record."""
        now = datetime.now(timezone.utc).isoformat()
        elder_id = data.get("elder_user_id") or data.get("user_id") or PRIMARY_USER_ID

        # Default notification preferences if not provided
        default_prefs = {
            "sms_enabled": True,
            "voice_enabled": False,
            "high_risk_enabled": True,
            "critical_risk_enabled": True,
            "quiet_hours_enabled": False,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "07:00",
            "max_notifications_per_hour": 5,
        }
        prefs = data.get("notification_preferences", {})
        merged_prefs = {**default_prefs, **prefs}

        record = {
            "caregiver_id": data["caregiver_id"],
            "elder_user_id": elder_id,
            "user_id": elder_id,  # backward compatibility
            "caregiver_user_id": data.get("caregiver_user_id"),
            "name": data["name"].strip(),
            "phone": data.get("phone", "").strip(),
            "email": data.get("email", "").strip().lower(),
            "relationship": data.get("relationship", "OTHER").upper(),
            "status": data.get("status", "PENDING").upper(),
            "is_verified": bool(data.get("is_verified", False)),
            "is_active": bool(data.get("is_active", True)),
            "isTrusted": bool(data.get("is_verified", False)),
            "verification_token": data.get("verification_token"),
            "verification_expires_at": data.get("verification_expires_at"),
            "notification_preferences": merged_prefs,
            "created_at": now,
            "updated_at": now,
        }
        self.collection.insert_one(record)
        return self.clean_doc(record) or {}

    def update_caregiver(self, caregiver_id: str, updates: dict) -> dict | None:
        """Partially update caregiver record."""
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        updates.pop("caregiver_id", None)
        updates.pop("elder_user_id", None)

        # If updating nested notification_preferences, merge carefully
        if "notification_preferences" in updates and isinstance(updates["notification_preferences"], dict):
            current = self.get_by_id(caregiver_id)
            if current:
                existing_prefs = current.get("notification_preferences", {})
                existing_prefs.update(updates["notification_preferences"])
                updates["notification_preferences"] = existing_prefs

        self.collection.update_one(
            {"caregiver_id": caregiver_id},
            {"$set": updates},
        )
        return self.get_by_id(caregiver_id)

    def delete_caregiver(self, caregiver_id: str) -> bool:
        """Deactivate or delete caregiver record."""
        result = self.collection.update_one(
            {"caregiver_id": caregiver_id},
            {"$set": {"is_active": False, "status": "DISABLED", "updated_at": datetime.now(timezone.utc).isoformat()}},
        )
        return result.modified_count > 0

    def verify_caregiver(self, caregiver_id: str) -> dict | None:
        """Mark caregiver relationship as verified."""
        now = datetime.now(timezone.utc).isoformat()
        self.collection.update_one(
            {"caregiver_id": caregiver_id},
            {
                "$set": {
                    "is_verified": True,
                    "isTrusted": True,
                    "status": "VERIFIED",
                    "verification_token": None,
                    "verified_at": now,
                    "updated_at": now,
                }
            },
        )
        return self.get_by_id(caregiver_id)

    def get_verified_caregivers_for_elder(self, elder_user_id: str) -> list[dict]:
        """Retrieve verified, active caregivers who are eligible for escalation alerts."""
        query = {
            "$and": [
                {
                    "$or": [
                        {"elder_user_id": elder_user_id},
                        {"user_id": elder_user_id},
                    ]
                },
                {"is_active": True},
                {
                    "$or": [
                        {"is_verified": True},
                        {"status": "VERIFIED"},
                        {"isTrusted": True},
                    ]
                },
            ]
        }
        cursor = self.collection.find(query)
        return self.clean_docs(list(cursor))
