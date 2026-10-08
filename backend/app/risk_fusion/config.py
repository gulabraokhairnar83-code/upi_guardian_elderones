"""UPI Guardian - Risk Fusion Engine Configuration.

Defines signal weights, cross-signal correlation parameters, risk thresholds,
and recommended action templates for the multi-signal risk fusion engine.
"""

from typing import Final


class RiskFusionConfig:
    """Central configuration for multi-signal risk calculation and thresholds."""

    # --------------------------------------------------------------------------
    # Signal Weights (Sum MUST equal 1.00 / 100%)
    # --------------------------------------------------------------------------
    # 1. Transaction Anomaly (Phase 4 Isolation Forest):
    # Core mathematical measure of divergence from normal user baseline (35%).
    WEIGHT_TRANSACTION_ANOMALY: float = 0.35

    # 2. Communication Risk (Phase 5 NLP TF-IDF + Logistic Regression):
    # Coercion, urgency, or impersonation detected in recent SMS / Call transcripts (30%).
    WEIGHT_COMMUNICATION_RISK: float = 0.30

    # 3. Behavioral Deviation (Z-score deviation):
    # Statistical amount anomaly relative to elder's specific historical spending (15%).
    WEIGHT_BEHAVIORAL_DEVIATION: float = 0.15

    # 4. New Payee Signal:
    # First-time or unfamiliar payee UPI ID / VPA increases vulnerability (8%).
    WEIGHT_NEW_PAYEE: float = 0.08

    # 5. Velocity Signal:
    # Rapid succession of transactions within a short window indicates fraud pressure (7%).
    WEIGHT_VELOCITY: float = 0.07

    # 6. Temporal Correlation Signal:
    # Mathematical proximity between a suspicious communication and a payment (5%).
    WEIGHT_TEMPORAL_CORRELATION: float = 0.05

    # --------------------------------------------------------------------------
    # Cross-Signal Correlation Boost
    # --------------------------------------------------------------------------
    # Maximum window backward from transaction timestamp to search for communication (minutes)
    COMMUNICATION_TRANSACTION_WINDOW_MINUTES: int = 120  # 2 hours

    # Boost added when BOTH high communication risk and high transaction anomaly co-occur
    CROSS_SIGNAL_BOOST: float = 10.0

    # Minimum thresholds required to qualify for cross-signal boost
    CROSS_SIGNAL_MIN_COMM_RISK: float = 60.0
    CROSS_SIGNAL_MIN_TX_ANOMALY: float = 60.0

    # --------------------------------------------------------------------------
    # Risk Level Boundaries (0.0 to 100.0 Scale)
    # --------------------------------------------------------------------------
    SCORE_LOW_MAX: float = 29.0       # 0.0 to 29.0: LOW
    SCORE_MEDIUM_MAX: float = 59.0    # 30.0 to 59.0: MEDIUM
    SCORE_HIGH_MAX: float = 84.0      # 60.0 to 84.0: HIGH
    # 85.0 to 100.0: CRITICAL

    # Threshold for generating automated family / caregiver alerts
    ALERT_TRIGGER_SCORE: float = 60.0

    # Alert types
    ALERT_TYPE_HIGH: str = "RISK_FUSION_HIGH"
    ALERT_TYPE_CRITICAL: str = "RISK_FUSION_CRITICAL"

    # --------------------------------------------------------------------------
    # Standard Action Guidance (Elder-Friendly Plain Language)
    # NOTE: Never say 'Fraud confirmed' or 'Compromised' (early-warning system).
    # --------------------------------------------------------------------------
    ACTION_LOW: str = "Continue normally, but remain alert."
    ACTION_MEDIUM: str = "Verify the transaction and communication through official channels."
    ACTION_HIGH: str = "Pause the transaction and verify the recipient and message through an official source."
    ACTION_CRITICAL: str = (
        "Do not proceed. Contact a trusted caregiver or official bank/UPI support "
        "using a verified contact method."
    )

    VERSION: str = "1.0.0"

    @classmethod
    def get_action_for_level(cls, risk_level: str) -> str:
        """Return standardized recommended action for a risk level."""
        level = (risk_level or "").upper()
        if level == "CRITICAL":
            return cls.ACTION_CRITICAL
        elif level == "HIGH":
            return cls.ACTION_HIGH
        elif level == "MEDIUM":
            return cls.ACTION_MEDIUM
        return cls.ACTION_LOW

    @classmethod
    def determine_risk_level(cls, score: float) -> str:
        """Map a 0-100 continuous score to discrete risk categories."""
        if score <= cls.SCORE_LOW_MAX:
            return "LOW"
        elif score <= cls.SCORE_MEDIUM_MAX:
            return "MEDIUM"
        elif score <= cls.SCORE_HIGH_MAX:
            return "HIGH"
        return "CRITICAL"
