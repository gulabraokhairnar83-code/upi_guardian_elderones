"""UPI Guardian - Transaction Service."""

from datetime import datetime, timezone
import time
from app.db.connection import get_db
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.transaction_repository import TransactionRepository
from app.ml.config import ALERT_TRIGGER_SCORE
from app.ml.inference.service import AnomalyDetectionService
from app.ml.models.isolation_forest import ModelNotTrainedError
from app.utils.errors import ModelNotAvailableError, NotFoundError

_repo = TransactionRepository()
_alert_repo = AlertRepository()
_ml_service = AnomalyDetectionService()


class TransactionService:
    """Business logic for transaction queries, retrieval, and ML anomaly detection."""

    @staticmethod
    def list_transactions(status: str | None = None, query: str | None = None) -> list[dict]:
        return _repo.list_transactions(status=status, query=query)

    @staticmethod
    def get_transaction(transaction_id: str) -> dict:
        transaction = _repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction with ID '{transaction_id}' was not found.")
        return transaction

    @staticmethod
    def analyze_transaction(payload: dict) -> dict:
        """Run ML transaction anomaly detection using scikit-learn Isolation Forest.

        Pipeline:
        1. Retrieve user historical baseline from database
        2. Extract 5 numerical features (amount, z-score, velocity, is_new_payee, unusual_time)
        3. Run Isolation Forest inference
        4. Derive 0-100 anomaly score and risk level (LOW/MEDIUM/HIGH/CRITICAL)
        5. Generate behavioral factor breakdown and human-readable explanation
        6. Store analyzed transaction in database (idempotent)
        7. Create alert idempotently if threshold is reached
        8. Return contract-compliant response
        """
        user_id = str(payload.get("user_id") or "usr_sunita_68").strip()
        txn_id = str(payload.get("transaction_id") or payload.get("transactionId") or f"TXN-UG-ANL-{int(time.time() * 1000)}").strip()

        # 1. Retrieve user historical context
        historical_stats = _repo.get_user_history_stats(user_id)

        # 2-5. Run ML inference pipeline
        try:
            analysis = _ml_service.analyze(
                transaction=payload,
                historical_stats=historical_stats,
            )
        except ModelNotTrainedError as exc:
            raise ModelNotAvailableError(str(exc)) from exc

        # Format temporal fields
        now_utc = datetime.now(timezone.utc)
        iso_timestamp = payload.get("timestamp") or now_utc.isoformat()
        time_str = payload.get("time") or now_utc.strftime("%I:%M %p")
        date_str = now_utc.strftime("%d %b %Y")

        # Map ML risk level to frontend status contract
        status_map = {
            "LOW": "safe",
            "MEDIUM": "review",
            "HIGH": "high",
            "CRITICAL": "critical",
        }
        frontend_status = status_map.get(analysis["risk_level"], "review")

        # 6. Build and persist analyzed transaction (idempotent)
        txn_record = {
            "id": txn_id,
            "user_id": user_id,
            "amount": float(payload["amount"]),
            "timestamp": iso_timestamp,
            "payee": payload["payee"],
            "transaction_type": payload.get("transaction_type", "P2P"),
            "is_new_payee": bool(analysis["features"]["is_new_payee"]),
            "historical_average": historical_stats["mean"],
            "historical_std_dev": historical_stats["std"],
            "behavioral_deviation": analysis["features"]["z_score_deviation"],
            "velocity": int(analysis["features"]["velocity"]),
            "unusual_time": bool(analysis["features"]["unusual_time"]),
            "anomaly_score": round(analysis["anomaly_score"] / 100.0, 2),
            "communication_risk": None,  # Reserved for Phase 5 NLP integration
            "final_risk_score": int(round(analysis["anomaly_score"])),
            "risk_level": frontend_status,
            "explanation": analysis["explanation"],
            "analyzed_at": now_utc.isoformat(),
            # Frontend presentation compatibility fields
            "date": date_str,
            "time": time_str,
            "location": payload.get("location", "Pune"),
            "risk": int(round(analysis["anomaly_score"])),
            "status": frontend_status,
            "newPayee": bool(analysis["features"]["is_new_payee"]),
            "upiId": payload["upiId"],
            "device": payload.get("device", "Sunita's phone"),
            "is_synthetic": False,
        }

        existing_txn = _repo.get_by_id(txn_id)
        if existing_txn:
            _repo.collection.update_one({"id": txn_id}, {"$set": txn_record})
        else:
            _repo.insert(txn_record)

        # 7. Alert creation (idempotent, prevents duplicates)
        alert_result = None
        should_alert = (
            analysis["anomaly_score"] >= ALERT_TRIGGER_SCORE
            or analysis["risk_level"] in ("HIGH", "CRITICAL")
        )

        if should_alert:
            existing_alert = _alert_repo.get_by_transaction_id(txn_id)
            if existing_alert:
                alert_result = existing_alert
            else:
                alert_level = "critical" if analysis["risk_level"] == "CRITICAL" else "high"
                title = (
                    "Critical transaction anomaly detected"
                    if alert_level == "critical"
                    else "Suspicious transaction anomaly detected"
                )
                new_alert = {
                    "user_id": user_id,
                    "transaction_id": txn_id,
                    "alert_type": "TRANSACTION_ANOMALY",
                    "level": alert_level,
                    "amount": float(payload["amount"]),
                    "title": title,
                    "detail": analysis["explanation"],
                    "time": "Just now",
                    "risk": int(round(analysis["anomaly_score"])),
                    "status": "pending",
                    "anomaly_score": analysis["anomaly_score"],
                    "contributing_factors": analysis["contributing_factors"],
                    "explanation": analysis["explanation"],
                    "created_at": now_utc.isoformat(),
                }
                alert_result = _alert_repo.insert_alert(new_alert)

                # Record event in risk_events collection
                try:
                    db = get_db()
                    db.risk_events.insert_one({
                        "event_id": f"re_anl_{int(time.time() * 1000)}",
                        "user_id": user_id,
                        "transaction_id": txn_id,
                        "time": time_str,
                        "text": f"Anomalous transaction of ₹{payload['amount']:,.2f} detected",
                        "event_type": "TRANSACTION_ANOMALY",
                        "risk_score": int(round(analysis["anomaly_score"])),
                        "created_at": now_utc.isoformat(),
                    })
                except Exception:
                    pass

        # 8. Return contract-compliant response
        return {
            "success": True,
            "transaction_id": txn_id,
            "transactionId": txn_id,
            "payee": payload["payee"],
            "amount": float(payload["amount"]),
            "riskScore": int(round(analysis["anomaly_score"])),
            "riskLevel": frontend_status,
            "recommendedAction": analysis["recommended_action"],
            "contributingFactors": [
                {"name": f["factor"], "score": f.get("value", 0)}
                for f in analysis["contributing_factors"]
            ],
            "explanation": analysis["explanation"],
            "analysis": {
                "anomaly_score": analysis["anomaly_score"],
                "anomaly": analysis["anomaly"],
                "risk_level": analysis["risk_level"],
                "model_version": analysis["model_version"],
                "features": analysis["features"],
                "contributing_factors": analysis["contributing_factors"],
                "explanation": analysis["explanation"],
                "recommended_action": analysis["recommended_action"],
            },
            "alert": alert_result,
        }
