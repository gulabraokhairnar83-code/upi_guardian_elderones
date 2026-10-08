"""UPI Guardian - Family & Caregiver Repository."""

from app.db.repositories.base_repository import BaseRepository
from app.db.seed_data import PRIMARY_USER_ID


class FamilyRepository(BaseRepository):
    """Data access layer for users and caregivers collections."""

    def __init__(self):
        super().__init__("users")

    def get_elder_profile(self, user_id: str = PRIMARY_USER_ID) -> dict | None:
        user = self.collection.find_one({"user_id": user_id})
        if not user:
            return None

        # Dynamically calculate current active alert count
        db = self.collection.database
        active_alerts = db.alerts.count_documents({"user_id": user_id, "status": "pending"})
        tx_count = db.transactions.count_documents({"user_id": user_id})

        return {
            "id": user.get("user_id", user_id),
            "name": user.get("name", "Sunita Devi"),
            "age": user.get("age", 68),
            "location": user.get("location", "Pune"),
            "accountSafetyStatus": user.get("accountSafetyStatus", "Protected"),
            "phone": user.get("phone", "+91 ••••• ••410"),
            "email": user.get("email", "sunita.demo@example.com"),
            "twoFactorEnabled": user.get("twoFactorEnabled", True),
            "loginAlertsEnabled": user.get("loginAlertsEnabled", True),
            "metrics": {
                "currentRiskScore": 27,
                "todayTransactionsCount": tx_count,
                "activeAlertsCount": active_alerts,
                "scamCommunicationsCount": 3,
            },
        }

    def resolve_family_alerts(self, user_id: str = PRIMARY_USER_ID) -> dict:
        db = self.collection.database
        db.alerts.update_many(
            {"user_id": user_id, "status": "pending"},
            {"$set": {"status": "resolved"}},
        )
        profile = self.get_elder_profile(user_id)
        if profile:
            profile["metrics"]["activeAlertsCount"] = 0
        return profile or {}

    def get_caregivers(self, user_id: str = PRIMARY_USER_ID) -> list[dict]:
        db = self.collection.database
        cursor = db.caregivers.find({"user_id": user_id})
        return self.clean_docs(list(cursor))
