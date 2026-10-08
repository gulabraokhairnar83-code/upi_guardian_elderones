"""UPI Guardian - User Repository."""

from datetime import datetime, timezone
import re
from app.db.repositories.base_repository import BaseRepository
from app.db.seed_data import PRIMARY_USER_ID


class UserRepository(BaseRepository):
    """Data access layer for users collection."""

    def __init__(self):
        super().__init__("users")

    def get_by_id(self, user_id: str) -> dict | None:
        """Retrieve user by user_id, stripping password_hash for safety."""
        pattern = {"$regex": f"^{re.escape(user_id.strip())}$", "$options": "i"}
        doc = self.collection.find_one({"$or": [{"user_id": pattern}, {"_id": pattern}]})
        cleaned = self.clean_doc(doc)
        if cleaned and "password_hash" in cleaned:
            del cleaned["password_hash"]
        return cleaned

    def get_by_id_with_auth(self, user_id: str) -> dict | None:
        """Internal helper retrieving user including password_hash."""
        pattern = {"$regex": f"^{re.escape(user_id.strip())}$", "$options": "i"}
        doc = self.collection.find_one({"$or": [{"user_id": pattern}, {"_id": pattern}]})
        return self.clean_doc(doc)

    def get_by_email(self, email: str) -> dict | None:
        """Retrieve user by normalized email (includes password_hash for authentication)."""
        clean_email = email.strip().lower()
        doc = self.collection.find_one({"email": clean_email})
        return self.clean_doc(doc)

    def get_by_phone(self, phone: str) -> dict | None:
        """Retrieve user by phone number."""
        clean_phone = phone.strip()
        doc = self.collection.find_one({"phone": clean_phone})
        cleaned = self.clean_doc(doc)
        if cleaned and "password_hash" in cleaned:
            del cleaned["password_hash"]
        return cleaned

    def create_user(self, user_data: dict) -> dict:
        """Persist new user document and return clean user representation."""
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "user_id": user_data["user_id"],
            "_id": user_data["user_id"],
            "name": user_data["name"].strip(),
            "email": user_data["email"].strip().lower(),
            "phone": user_data.get("phone", "").strip(),
            "password_hash": user_data["password_hash"],
            "role": user_data.get("role", "ELDER").upper(),
            "is_active": user_data.get("is_active", True),
            "accountSafetyStatus": user_data.get("accountSafetyStatus", "Protected"),
            "created_at": now,
            "updated_at": now,
        }
        self.collection.insert_one(record)
        return self.get_by_id(user_data["user_id"]) or {}

    def update_user(self, user_id: str, updates: dict) -> dict | None:
        """Update user record and return updated document."""
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        # Protect user_id and _id from alteration
        updates.pop("user_id", None)
        updates.pop("_id", None)

        self.collection.update_one(
            {"user_id": user_id},
            {"$set": updates},
        )
        return self.get_by_id(user_id)

    def count(self, filter_criteria: dict | None = None) -> int:
        return self.collection.count_documents(filter_criteria or {})
