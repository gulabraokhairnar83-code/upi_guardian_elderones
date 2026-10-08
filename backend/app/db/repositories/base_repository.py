"""UPI Guardian - Base Repository Helper."""

from app.db.connection import get_db


class BaseRepository:
    """Base class for MongoDB collection operations."""

    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    @property
    def collection(self):
        return get_db()[self.collection_name]

    @staticmethod
    def clean_doc(doc: dict | None) -> dict | None:
        """Strip MongoDB internal _id field or format it cleanly for JSON serialization."""
        if not doc:
            return None
        cleaned = dict(doc)
        if "_id" in cleaned:
            del cleaned["_id"]
        return cleaned

    @classmethod
    def clean_docs(cls, docs: list[dict]) -> list[dict]:
        return [cls.clean_doc(d) for d in docs if d is not None]
