"""UPI Guardian - Risk Fusion Data Models & Schemas."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class RiskSignals:
    """Normalized multi-signal inputs (each 0.0 to 100.0)."""

    transaction_anomaly_score: float = 0.0
    communication_risk_score: float = 0.0
    behavioral_deviation_score: float = 0.0
    new_payee_score: float = 0.0
    velocity_score: float = 0.0
    temporal_correlation_score: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "transaction_anomaly_score": round(float(self.transaction_anomaly_score), 1),
            "communication_risk_score": round(float(self.communication_risk_score), 1),
            "behavioral_deviation_score": round(float(self.behavioral_deviation_score), 1),
            "new_payee_score": round(float(self.new_payee_score), 1),
            "velocity_score": round(float(self.velocity_score), 1),
            "temporal_correlation_score": round(float(self.temporal_correlation_score), 1),
        }


@dataclass
class TemporalMatch:
    """Result of temporal correlation lookup."""

    temporal_score: float = 0.0
    delta_minutes: float | None = None
    matched_communication_id: str | None = None
    matched_message_type: str | None = None
    matched_scam_probability: float = 0.0
    within_window: bool = False
    qualifies_for_boost: bool = False


@dataclass
class RiskFusionResult:
    """Final output of the Risk Fusion Engine."""

    transaction_id: str
    user_id: str
    signals: RiskSignals
    correlation_boost: float
    raw_weighted_score: float
    final_risk_score: float
    risk_level: str
    top_contributing_factors: list[str]
    explanation: str
    recommended_action: str
    matched_communication_id: str | None = None
    alert_created: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert result to API / storage dictionary."""
        sig_dict = self.signals.to_dict()
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "transaction_anomaly_score": sig_dict["transaction_anomaly_score"],
            "communication_risk_score": sig_dict["communication_risk_score"],
            "behavioral_deviation_score": sig_dict["behavioral_deviation_score"],
            "new_payee_score": sig_dict["new_payee_score"],
            "velocity_score": sig_dict["velocity_score"],
            "temporal_correlation_score": sig_dict["temporal_correlation_score"],
            "correlation_boost": round(float(self.correlation_boost), 1),
            "final_risk_score": round(float(self.final_risk_score), 1),
            "risk_level": self.risk_level,
            "top_contributing_factors": self.top_contributing_factors,
            "explanation": self.explanation,
            "recommended_action": self.recommended_action,
            "communication_id": self.matched_communication_id,
            "alert_created": self.alert_created,
        }
