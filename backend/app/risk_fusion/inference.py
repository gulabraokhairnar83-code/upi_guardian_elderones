"""UPI Guardian - Risk Fusion Service.

Orchestrates multi-signal fusion by synthesizing Phase 4 Isolation Forest anomaly output,
Phase 5 NLP scam classification, temporal proximity, behavioral deviation, payee novelty,
and velocity into an explainable composite risk score.
"""

from datetime import datetime, timezone
import time
from typing import Any
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.message_repository import MessageRepository
from app.db.repositories.risk_event_repository import RiskEventRepository
from app.db.repositories.transaction_repository import TransactionRepository
from app.ml.inference.service import AnomalyDetectionService
from app.ml.models.isolation_forest import ModelNotTrainedError
from app.risk_fusion.config import RiskFusionConfig
from app.risk_fusion.correlation import TemporalCorrelationEngine
from app.risk_fusion.explainer import RiskFusionExplainer
from app.risk_fusion.models import RiskFusionResult, RiskSignals, TemporalMatch
from app.risk_fusion.scoring import RiskScoringEngine
from app.utils.errors import ModelNotAvailableError, NotFoundError, ValidationError


class RiskFusionService:
    """Central coordinator for multi-signal composite risk assessment."""

    def __init__(
        self,
        tx_repo: TransactionRepository | None = None,
        msg_repo: MessageRepository | None = None,
        alert_repo: AlertRepository | None = None,
        risk_event_repo: RiskEventRepository | None = None,
        ml_service: AnomalyDetectionService | None = None,
    ):
        self.tx_repo = tx_repo or TransactionRepository()
        self.msg_repo = msg_repo or MessageRepository()
        self.alert_repo = alert_repo or AlertRepository()
        self.risk_event_repo = risk_event_repo or RiskEventRepository()
        self.ml_service = ml_service or AnomalyDetectionService()

    def analyze_transaction_risk(
        self,
        transaction_data: dict[str, Any],
        user_id: str | None = None,
        candidate_communications: list[dict[str, Any]] | None = None,
        create_alert_if_needed: bool = True,
        persist_event: bool = True,
    ) -> dict[str, Any]:
        """Perform full multi-signal fused risk analysis on a transaction.

        Args:
            transaction_data: Dict containing transaction details (amount, payee, etc.)
                              OR containing a 'transaction_id' to load from DB.
            user_id: User identifier (defaults to transaction's user_id or 'usr_sunita_68')
            candidate_communications: Optional explicit communication list for testing
            create_alert_if_needed: Whether to trigger alerts for HIGH/CRITICAL events
            persist_event: Whether to persist into the risk_events collection

        Returns:
            Dictionary matching the Phase 6 API analysis contract.
        """
        # 1. Resolve transaction record
        tx_id = (
            transaction_data.get("transaction_id")
            or transaction_data.get("transactionId")
            or transaction_data.get("id")
        )
        resolved_user_id = str(
            user_id
            or transaction_data.get("user_id")
            or transaction_data.get("userId")
            or "usr_sunita_68"
        ).strip()

        # If minimal dict with just transaction_id was supplied, look up from DB
        if tx_id and ("amount" not in transaction_data or "payee" not in transaction_data):
            existing_txn = self.tx_repo.get_by_id(str(tx_id))
            if not existing_txn:
                raise NotFoundError(f"Transaction with ID '{tx_id}' was not found in the database.")
            # Merge existing record with any overrides
            tx_record = {**existing_txn, **transaction_data}
            if not resolved_user_id or resolved_user_id == "usr_sunita_68":
                resolved_user_id = existing_txn.get("user_id", resolved_user_id)
        else:
            tx_record = dict(transaction_data)
            if not tx_id:
                tx_id = f"TXN-UG-FUS-{int(time.time() * 1000)}"
                tx_record["id"] = tx_id
                tx_record["transaction_id"] = tx_id

        # 2. Retrieve historical baseline
        historical_stats = self.tx_repo.get_user_history_stats(resolved_user_id)

        # 3. Phase 4 Isolation Forest Transaction Anomaly
        try:
            ml_analysis = self.ml_service.analyze(
                transaction=tx_record,
                historical_stats=historical_stats,
            )
        except ModelNotTrainedError as exc:
            raise ModelNotAvailableError(str(exc)) from exc

        tx_anomaly_score = float(ml_analysis["anomaly_score"])
        features = ml_analysis["features"]
        unusual_time = bool(features.get("unusual_time", 0))

        # 4. Phase 5 NLP & Temporal Correlation
        tx_timestamp = tx_record.get("timestamp") or tx_record.get("time") or datetime.now(timezone.utc).isoformat()
        temporal_match: TemporalMatch = TemporalCorrelationEngine.find_temporal_correlation(
            user_id=resolved_user_id,
            transaction_timestamp=tx_timestamp,
            candidate_communications=candidate_communications,
            message_repo=self.msg_repo,
        )

        # 5. Extract and normalize the 6 multi-signals
        sig_tx = RiskScoringEngine.normalize_transaction_anomaly(tx_anomaly_score)
        sig_comm = RiskScoringEngine.normalize_communication_risk(temporal_match.matched_scam_probability)
        sig_beh = RiskScoringEngine.normalize_behavioral_deviation(features.get("z_score_deviation"))
        sig_payee = RiskScoringEngine.normalize_new_payee(features.get("is_new_payee"))
        sig_vel = RiskScoringEngine.normalize_velocity(features.get("velocity"))
        sig_temp = round(temporal_match.temporal_score, 1)

        signals = RiskSignals(
            transaction_anomaly_score=sig_tx,
            communication_risk_score=sig_comm,
            behavioral_deviation_score=sig_beh,
            new_payee_score=sig_payee,
            velocity_score=sig_vel,
            temporal_correlation_score=sig_temp,
        )

        # 6. Weighted multi-signal fusion
        weighted_score = RiskScoringEngine.compute_weighted_score(signals)

        # 7. Cross-signal correlation boost (+10 if high comm + high tx within 2h)
        final_score, boost = RiskScoringEngine.apply_cross_signal_boost(
            signals=signals,
            weighted_score=weighted_score,
            delta_minutes=temporal_match.delta_minutes,
        )

        # 8. Determine final risk level
        risk_level = RiskFusionConfig.determine_risk_level(final_score)

        # 9. Explainability
        explanation_data = RiskFusionExplainer.explain(
            signals=signals,
            risk_level=risk_level,
            correlation_boost=boost,
            unusual_time=unusual_time,
        )

        # 10. Alert creation & deduplication
        alert_created = False
        if create_alert_if_needed and risk_level in ("HIGH", "CRITICAL"):
            existing_alert = self.alert_repo.get_by_transaction_id(str(tx_id))
            if not existing_alert:
                alert_type = (
                    RiskFusionConfig.ALERT_TYPE_CRITICAL
                    if risk_level == "CRITICAL"
                    else RiskFusionConfig.ALERT_TYPE_HIGH
                )
                level_str = "critical" if risk_level == "CRITICAL" else "high"
                title = (
                    "Critical multi-signal risk detected"
                    if risk_level == "CRITICAL"
                    else "High-risk transaction activity detected"
                )
                amt = float(tx_record.get("amount", 0.0))

                self.alert_repo.insert_alert({
                    "user_id": resolved_user_id,
                    "transaction_id": str(tx_id),
                    "alert_type": alert_type,
                    "level": level_str,
                    "amount": amt,
                    "title": title,
                    "detail": explanation_data["explanation"],
                    "time": "Just now",
                    "risk": int(round(final_score)),
                    "status": "pending",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "is_synthetic": False,
                })
                alert_created = True

        # 11. Build fusion result
        result = RiskFusionResult(
            transaction_id=str(tx_id),
            user_id=resolved_user_id,
            signals=signals,
            correlation_boost=boost,
            raw_weighted_score=weighted_score,
            final_risk_score=final_score,
            risk_level=risk_level,
            top_contributing_factors=explanation_data["top_contributing_factors"],
            explanation=explanation_data["explanation"],
            recommended_action=explanation_data["recommended_action"],
            matched_communication_id=temporal_match.matched_communication_id,
            alert_created=alert_created,
        )

        # 12. Persist to risk_events collection
        if persist_event:
            self.risk_event_repo.save_risk_event(result.to_dict())

        # 13. Phase 8: Caregiver Escalation for HIGH and CRITICAL risks
        level_str = str(result.risk_level).upper()
        if level_str in ("HIGH", "CRITICAL"):
            try:
                from app.notifications.escalation_service import EscalationService
                EscalationService.escalate_risk_event(result.to_dict(), user_id=resolved_user_id)
            except Exception as exc:
                import logging
                logging.getLogger("upi_guardian.risk_fusion").warning("Caregiver escalation skipped/failed: %s", exc)

        return result.to_dict()
