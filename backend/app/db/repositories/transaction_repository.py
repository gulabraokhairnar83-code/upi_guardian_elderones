"""UPI Guardian - Transaction Repository."""

import re
from app.db.repositories.base_repository import BaseRepository


class TransactionRepository(BaseRepository):
    """Data access layer for transactions collection."""

    def __init__(self):
        super().__init__("transactions")

    def list_transactions(self, status: str | None = None, query: str | None = None) -> list[dict]:
        filter_criteria: dict = {}
        if status and status != "all":
            filter_criteria["status"] = status.lower()

        if query and query.strip():
            escaped = re.escape(query.strip())
            pattern = {"$regex": escaped, "$options": "i"}
            filter_criteria["$or"] = [{"payee": pattern}, {"id": pattern}]

        cursor = self.collection.find(filter_criteria).sort("id", 1)
        return self.clean_docs(list(cursor))

    def get_by_id(self, transaction_id: str) -> dict | None:
        pattern = {"$regex": f"^{re.escape(transaction_id.strip())}$", "$options": "i"}
        doc = self.collection.find_one({"id": pattern})
        return self.clean_doc(doc)

    def insert(self, data: dict) -> dict:
        self.collection.insert_one(data)
        return self.clean_doc(data)

    def count(self, filter_criteria: dict | None = None) -> int:
        return self.collection.count_documents(filter_criteria or {})

    def get_user_history_stats(self, user_id: str) -> dict:
        """Calculate historical baseline statistics (mean, std, known payees) for a user."""
        txns = list(self.collection.find({"user_id": user_id}))
        if not txns:
            # Baseline fallback for new or unseeded user
            return {
                "mean": 2850.0,
                "std": 1120.0,
                "known_payees": set(),
                "count": 0,
            }

        amounts = [float(t["amount"]) for t in txns if t.get("amount") is not None and float(t["amount"]) > 0]
        if not amounts:
            mean = 2850.0
            std = 1120.0
        elif len(amounts) == 1:
            mean = amounts[0]
            std = 0.0
        else:
            mean = float(sum(amounts) / len(amounts))
            variance = sum((x - mean) ** 2 for x in amounts) / (len(amounts) - 1)
            std = float(variance ** 0.5)

        known_payees = set()
        for t in txns:
            if t.get("payee"):
                known_payees.add(str(t["payee"]).strip())
            if t.get("upiId"):
                known_payees.add(str(t["upiId"]).strip())

        return {
            "mean": round(mean, 2),
            "std": round(std, 2),
            "known_payees": known_payees,
            "count": len(amounts),
        }
