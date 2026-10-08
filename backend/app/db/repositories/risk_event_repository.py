"""UPI Guardian - Risk Event Repository.

Provides data access and persistence for the 'risk_events' collection,
recording multi-signal fused risk assessments and audit trails.
"""

from datetime import datetime, timezone
import uuid
from typing import Any
from app.db.repositories.base_repository import BaseRepository


class RiskEventRepository(BaseRepository):
    """Data access layer for risk_events collection."""

    def __init__(self):
        super().__init__("risk_events")

    def save_risk_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Save a new risk event record.

        Guarantees:
        - Unique string identifier
        - UTC ISO timestamps for indexing
        - MongoDB _id sanitization
        """
        record = dict(event_data)
        event_id = record.get("event_id") or record.get("id") or f"re_{uuid.uuid4().hex[:12]}"
        now_utc = datetime.now(timezone.utc).isoformat()

        record["id"] = event_id
        record["event_id"] = event_id
        if "created_at" not in record:
            record["created_at"] = now_utc
        if "timestamp" not in record:
            record["timestamp"] = record["created_at"]

        # If a record for this transaction already exists, update it; otherwise insert
        tx_id = record.get("transaction_id")
        if tx_id:
            existing = self.collection.find_one({"transaction_id": tx_id})
            if existing:
                self.collection.update_one({"transaction_id": tx_id}, {"$set": record})
                return self.clean_doc(record)

        self.collection.insert_one(record)
        return self.clean_doc(record)

    def get_by_id(self, event_id: str) -> dict[str, Any] | None:
        """Find event by either id or event_id."""
        doc = self.collection.find_one({"$or": [{"id": event_id}, {"event_id": event_id}]})
        return self.clean_doc(doc)

    def get_by_transaction_id(self, transaction_id: str) -> dict[str, Any] | None:
        """Find event by associated transaction ID."""
        doc = self.collection.find_one({"transaction_id": transaction_id})
        return self.clean_doc(doc)

    def list_events(
        self,
        user_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List recent risk events in reverse chronological order."""
        query = {"user_id": user_id} if user_id else {}
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        return self.clean_docs(list(cursor))

    def count_high_or_critical(self, user_id: str | None = None) -> int:
        """Count active high or critical risk events."""
        query: dict[str, Any] = {
            "$or": [
                {"risk_level": {"$in": ["HIGH", "CRITICAL"]}},
                {"final_risk_score": {"$gte": 60.0}},
            ]
        }
        if user_id:
            query["user_id"] = user_id
        return self.collection.count_documents(query)
