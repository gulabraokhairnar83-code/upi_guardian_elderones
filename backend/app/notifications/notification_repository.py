"""UPI Guardian - Notification Repository."""

from datetime import datetime, timezone, timedelta
import re
from app.db.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    """Data access layer for notifications collection."""

    def __init__(self):
        super().__init__("notifications")

    def get_by_id(self, notification_id: str) -> dict | None:
        """Find notification by notification_id."""
        pattern = {"$regex": f"^{re.escape(notification_id.strip())}$", "$options": "i"}
        doc = self.collection.find_one({"notification_id": pattern})
        return self.clean_doc(doc)

    def list_by_user(self, user_id: str, limit: int = 50) -> list[dict]:
        """List notifications for an elder user or caregiver."""
        query = {
            "$or": [
                {"user_id": user_id},
                {"elder_user_id": user_id},
                {"caregiver_id": user_id},
                {"caregiver_user_id": user_id},
            ]
        }
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        return self.clean_docs(list(cursor))

    def find_duplicate(self, risk_event_id: str, caregiver_id: str, channel: str) -> dict | None:
        """Find an existing notification for the same event, caregiver, and channel.

        Prevents duplicate dispatches.
        """
        if not risk_event_id or not caregiver_id:
            return None
        doc = self.collection.find_one({
            "risk_event_id": risk_event_id,
            "caregiver_id": caregiver_id,
            "channel": channel,
            "status": {"$in": ["SENT", "DELIVERED", "SENDING", "PENDING"]},
        })
        return self.clean_doc(doc)

    def count_caregiver_notifications_in_window(self, caregiver_id: str, hours: int = 1) -> int:
        """Count notifications sent to a caregiver in the last N hours for rate limiting."""
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        count = self.collection.count_documents({
            "caregiver_id": caregiver_id,
            "created_at": {"$gte": cutoff},
            "status": {"$in": ["SENT", "DELIVERED", "SENDING", "PENDING"]},
        })
        return count

    def create_notification(self, data: dict) -> dict:
        """Record a notification dispatch attempt."""
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "notification_id": data["notification_id"],
            "user_id": data.get("user_id"),
            "elder_user_id": data.get("user_id"),
            "caregiver_id": data.get("caregiver_id"),
            "caregiver_user_id": data.get("caregiver_user_id"),
            "transaction_id": data.get("transaction_id"),
            "risk_event_id": data.get("risk_event_id"),
            "channel": data.get("channel"),
            "notification_type": data.get("notification_type", "RISK_ALERT"),
            "risk_level": data.get("risk_level"),
            "status": data.get("status", "PENDING"),
            "provider_message_id": data.get("provider_message_id"),
            "message_preview": data.get("message_preview"),
            "is_acknowledged": False,
            "acknowledged_at": None,
            "acknowledged_by": None,
            "error_code": data.get("error_code"),
            "created_at": now,
            "sent_at": now if data.get("status") == "SENT" else None,
            "failed_at": now if data.get("status") == "FAILED" else None,
            "delivered_at": None,
        }
        self.collection.insert_one(record)
        return self.clean_doc(record) or {}

    def acknowledge_notification(self, notification_id: str, acknowledged_by: str) -> dict | None:
        """Mark notification as acknowledged by caregiver or elder."""
        now = datetime.now(timezone.utc).isoformat()
        pattern = {"$regex": f"^{re.escape(notification_id.strip())}$", "$options": "i"}
        result = self.collection.update_one(
            {"notification_id": pattern},
            {
                "$set": {
                    "is_acknowledged": True,
                    "acknowledged_at": now,
                    "acknowledged_by": acknowledged_by,
                }
            },
        )
        if result.matched_count == 0:
            return None
        return self.get_by_id(notification_id)

    def update_delivery_status(self, provider_message_id: str, status: str, error: str | None = None) -> dict | None:
        """Update notification status from delivery receipt callback (e.g., Twilio webhook)."""
        if not provider_message_id:
            return None
        now = datetime.now(timezone.utc).isoformat()
        status_clean = status.upper().strip()
        update_fields: dict = {"status": status_clean}
        if status_clean == "DELIVERED":
            update_fields["delivered_at"] = now
        elif status_clean in ("FAILED", "UNDELIVERED"):
            update_fields["failed_at"] = now
            if error:
                update_fields["error_code"] = str(error)[:100]

        result = self.collection.update_one(
            {"provider_message_id": provider_message_id.strip()},
            {"$set": update_fields},
        )
        if result.matched_count == 0:
            return None
        doc = self.collection.find_one({"provider_message_id": provider_message_id.strip()})
        return self.clean_doc(doc)
