"""UPI Guardian - Alert Repository."""

from app.db.repositories.base_repository import BaseRepository


class AlertRepository(BaseRepository):
    """Data access layer for alerts collection."""

    def __init__(self):
        super().__init__("alerts")

    def list_alerts(self, level: str | None = None) -> list[dict]:
        filter_criteria = {}
        if level and level != "all":
            filter_criteria["level"] = level.lower()
        cursor = self.collection.find(filter_criteria).sort("id", 1)
        return self.clean_docs(list(cursor))

    def get_by_id(self, alert_id: int) -> dict | None:
        doc = self.collection.find_one({"id": alert_id})
        return self.clean_doc(doc)

    def resolve_alert(self, alert_id: int) -> dict | None:
        result = self.collection.find_one_and_update(
            {"id": alert_id},
            {"$set": {"status": "resolved"}},
            return_document=True,
        )
        return self.clean_doc(result)

    def count_active(self) -> int:
        return self.collection.count_documents({"status": "pending"})

    def get_by_transaction_id(self, transaction_id: str) -> dict | None:
        """Find existing alert associated with transaction_id to prevent duplicates."""
        doc = self.collection.find_one({"transaction_id": transaction_id})
        return self.clean_doc(doc)

    def get_by_message_hash(self, text_hash: str) -> dict | None:
        """Find existing alert associated with message text hash to prevent duplicates."""
        doc = self.collection.find_one({"text_hash": text_hash})
        return self.clean_doc(doc)

    def insert_alert(self, alert_data: dict) -> dict:
        """Insert a new alert with auto-incrementing integer id if not provided."""
        if "id" not in alert_data:
            last = self.collection.find_one(sort=[("id", -1)])
            next_id = (last["id"] + 1) if (last and "id" in last and isinstance(last["id"], int)) else 1
            alert_data["id"] = next_id

        self.collection.insert_one(alert_data)
        return self.clean_doc(alert_data)
