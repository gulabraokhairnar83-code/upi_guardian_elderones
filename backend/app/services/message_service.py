"""UPI Guardian - Message & Communication Analysis Service.

Coordinates real-time NLP inference for SMS messages and phone call transcripts,
MongoDB audit logging with text hashing, and idempotent alert creation.
"""

from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.message_repository import MessageRepository
from app.nlp.config import ALERT_TRIGGER_SCORE
from app.nlp.inference.service import NLPScamDetectionService
from app.nlp.models.scam_classifier import NLPModelNotTrainedError
from app.utils.errors import ModelNotAvailableError

_repo = MessageRepository()
_alert_repo = AlertRepository()
_nlp_service = NLPScamDetectionService()


class MessageService:
    """Service providing message scam analysis, audit persistence, and alerting."""

    @staticmethod
    def analyze_message(payload: dict) -> dict:
        """Analyze an SMS or call transcript using TF-IDF + Logistic Regression NLP pipeline.

        Pipeline:
        1. Clean and normalize communication text
        2. Compute SHA-256 text hash for privacy-safe deduplication
        3. Transform text using fitted TF-IDF vectorizer
        4. Predict class probabilities with Logistic Regression
        5. Map scam probability estimate (0-100) and risk level
        6. Perform rule-based explainability (categories, phrases, elder advice)
        7. Persist analysis into MongoDB 'analyzed_messages'
        8. Idempotently trigger alert if risk threshold is reached
        9. Return contract-compliant response
        """
        raw_text = payload["text"]
        msg_type = payload.get("message_type") or payload.get("type", "sms")
        user_id = str(payload.get("user_id") or "usr_sunita_68").strip()

        # Run NLP inference
        try:
            analysis = _nlp_service.analyze(text=raw_text, message_type=msg_type)
        except NLPModelNotTrainedError as exc:
            raise ModelNotAvailableError(str(exc)) from exc

        # Persist into MongoDB idempotently
        saved_record = _repo.save_nlp_analysis(
            user_id=user_id,
            text_hash=analysis["text_hash"],
            analysis=analysis,
        )

        # Alert creation (idempotent duplicate prevention)
        alert_result = None
        should_alert = (
            analysis["scam_probability"] >= ALERT_TRIGGER_SCORE
            or analysis["risk_level"] in ("HIGH", "CRITICAL")
            or analysis["classification"] == "SCAM"
        )

        if should_alert:
            existing_alert = _alert_repo.get_by_message_hash(analysis["text_hash"])
            if existing_alert:
                alert_result = existing_alert
            else:
                alert_level = "critical" if analysis["risk_level"] == "CRITICAL" else "high"
                new_alert = {
                    "user_id": user_id,
                    "message_id": saved_record.get("id"),
                    "text_hash": analysis["text_hash"],
                    "alert_type": "SCAM_COMMUNICATION",
                    "level": alert_level,
                    "title": "Suspicious communication detected",
                    "detail": analysis["explanation"],
                    "time": "Just now",
                    "risk": int(round(analysis["scam_probability"])),
                    "status": "pending",
                    "scam_probability": analysis["scam_probability"],
                    "categories": analysis["categories"],
                    "suspicious_phrases": analysis["suspicious_phrases"],
                    "explanation": analysis["explanation"],
                }
                alert_result = _alert_repo.insert_alert(new_alert)

        # Status and title mapping for frontend presentation
        is_suspicious = analysis["classification"] in ("SUSPICIOUS", "SCAM")
        level_map = {
            "LOW": "safe",
            "MEDIUM": "review",
            "HIGH": "high",
            "CRITICAL": "critical",
        }
        frontend_level = level_map.get(analysis["risk_level"], "safe")

        if analysis["classification"] == "SCAM":
            title = "POTENTIAL SCAM DETECTED"
        elif analysis["classification"] == "SUSPICIOUS":
            title = "SUSPICIOUS COMMUNICATION DETECTED"
        else:
            title = "NORMAL COMMUNICATION VERIFIED"

        return {
            "success": True,
            "isSuspicious": is_suspicious,
            "riskScore": int(round(analysis["scam_probability"])),
            "level": frontend_level,
            "title": title,
            "detectedPatterns": analysis["categories"],
            "explanation": analysis["explanation"],
            "recommendations": [analysis["recommended_action"]],
            "analysis": {
                "classification": analysis["classification"],
                "scam_probability": analysis["scam_probability"],
                "risk_level": analysis["risk_level"],
                "message_type": analysis["message_type"],
                "categories": analysis["categories"],
                "suspicious_phrases": analysis["suspicious_phrases"],
                "explanation": analysis["explanation"],
                "recommended_action": analysis["recommended_action"],
            },
            "alert": alert_result,
            "isDevelopmentStub": False,
        }

    @staticmethod
    def analyze_message_stub(payload: dict) -> dict:
        """Redirect legacy stub calls to real NLP pipeline."""
        return MessageService.analyze_message(payload)
