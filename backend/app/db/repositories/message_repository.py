"""UPI Guardian - Analyzed Message Repository.

Manages persistence and idempotent duplicate analysis lookups for the
'analyzed_messages' collection.
"""

from datetime import datetime, timezone
import uuid
from app.db.repositories.base_repository import BaseRepository
from app.db.seed_data import PRIMARY_USER_ID
from app.nlp.config import MODEL_VERSION


class MessageRepository(BaseRepository):
    """Data access layer for analyzed_messages collection."""

    def __init__(self):
        super().__init__("analyzed_messages")

    def find_by_hash(
        self,
        user_id: str,
        text_hash: str,
        model_version: str = MODEL_VERSION,
    ) -> dict | None:
        """Find existing analysis record by user_id, text_hash, and model_version for idempotency."""
        doc = self.collection.find_one({
            "user_id": user_id,
            "text_hash": text_hash,
            "model_version": model_version,
        })
        return self.clean_doc(doc)

    def save_nlp_analysis(
        self,
        user_id: str,
        text_hash: str,
        analysis: dict,
        message_id: str | None = None,
    ) -> dict:
        """Save or update an NLP message analysis record idempotently."""
        existing = self.find_by_hash(user_id, text_hash, analysis.get("model_version", MODEL_VERSION))
        now_utc = datetime.now(timezone.utc).isoformat()
        mid = message_id or (existing["id"] if existing else f"msg_{uuid.uuid4().hex[:12]}")

        record = {
            "id": mid,
            "message_id": mid,
            "user_id": user_id,
            "message_type": analysis.get("message_type", "sms"),
            "text_hash": text_hash,
            "classification": analysis.get("classification", "NORMAL"),
            "scam_probability": analysis.get("scam_probability", 0.0),
            "risk_level": analysis.get("risk_level", "LOW"),
            "categories": analysis.get("categories", []),
            "suspicious_phrases": analysis.get("suspicious_phrases", []),
            "explanation": analysis.get("explanation", ""),
            "recommended_action": analysis.get("recommended_action", ""),
            "model_version": analysis.get("model_version", MODEL_VERSION),
            "analyzed_at": now_utc,
            # Presentation compatibility fields
            "is_suspicious": analysis.get("classification") in ("SUSPICIOUS", "SCAM"),
            "level": "critical" if analysis.get("risk_level") == "CRITICAL" else (
                "high" if analysis.get("risk_level") == "HIGH" else (
                    "review" if analysis.get("risk_level") == "MEDIUM" else "safe"
                )
            ),
            "is_synthetic": False,
        }

        if existing:
            self.collection.update_one({"id": mid}, {"$set": record})
        else:
            self.collection.insert_one(record)

        return self.clean_doc(record)

    def save_analysis(self, payload: dict, result: dict, user_id: str = PRIMARY_USER_ID) -> dict:
        """Legacy helper for backward compatibility."""
        mid = f"msg_{uuid.uuid4().hex[:12]}"
        record = {
            "id": mid,
            "message_id": mid,
            "user_id": user_id,
            "text": payload.get("text", ""),
            "text_hash": str(hash(payload.get("text", ""))),
            "type": payload.get("type", "sms"),
            "message_type": payload.get("message_type", payload.get("type", "sms")),
            "risk_score": result.get("riskScore", 0),
            "level": result.get("level", "safe"),
            "is_suspicious": result.get("isSuspicious", False),
            "detected_patterns": result.get("detectedPatterns", []),
            "explanation": result.get("explanation", ""),
            "recommendations": result.get("recommendations", []),
            "is_development_stub": result.get("isDevelopmentStub", False),
            "is_synthetic": True,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.collection.insert_one(record)
        return self.clean_doc(record)
