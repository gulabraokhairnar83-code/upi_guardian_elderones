"""UPI Guardian - Multi-Signal Risk Scoring Engine.

Implements transparent, weighted multi-signal aggregation, normalization,
cross-signal correlation boost, and score clamping.
"""

import math
from app.risk_fusion.config import RiskFusionConfig
from app.risk_fusion.models import RiskSignals


class RiskScoringEngine:
    """Mathematical engine for normalizing signals and computing fused risk scores."""

    @staticmethod
    def clamp_score(score: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """Guarantee score is a finite float bounded within [min_val, max_val]."""
        try:
            val = float(score)
            if math.isnan(val) or math.isinf(val):
                return min_val
            return max(min_val, min(max_val, val))
        except (ValueError, TypeError):
            return min_val

    @classmethod
    def normalize_transaction_anomaly(cls, raw_score: float | int | None) -> float:
        """Normalize transaction anomaly score to 0.0 - 100.0 scale."""
        if raw_score is None:
            return 0.0
        val = float(raw_score)
        # Handle 0.0 - 1.0 probability if passed instead of 0 - 100
        if 0.0 < val <= 1.0:
            val = val * 100.0
        return round(cls.clamp_score(val), 2)

    @classmethod
    def normalize_communication_risk(cls, raw_score: float | int | None) -> float:
        """Normalize NLP scam probability score to 0.0 - 100.0 scale."""
        if raw_score is None:
            return 0.0
        val = float(raw_score)
        if 0.0 < val <= 1.0:
            val = val * 100.0
        return round(cls.clamp_score(val), 2)

    @classmethod
    def normalize_behavioral_deviation(cls, raw_deviation: float | int | None) -> float:
        """Normalize behavioral z-score deviation or score to 0.0 - 100.0 scale.

        Statistical z-scores typically range from 0 to ~4+.
        Scaling: |z| * 25.0 maps z=2 (95th percentile) to 50, z=4 (extreme) to 100.
        If value is already > 10.0, treat as already scaled score.
        """
        if raw_deviation is None:
            return 0.0
        try:
            val = abs(float(raw_deviation))
            if math.isnan(val) or math.isinf(val):
                return 0.0
            if val <= 10.0:
                scaled = val * 25.0
            else:
                scaled = val
            return round(cls.clamp_score(scaled), 2)
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def normalize_new_payee(cls, is_new: bool | int | float | None) -> float:
        """Normalize new/unusual payee indicator (100.0 if new, 0.0 if known)."""
        if is_new is None:
            return 0.0
        if isinstance(is_new, bool):
            return 100.0 if is_new else 0.0
        try:
            val = float(is_new)
            if val > 1.0:
                return round(cls.clamp_score(val), 2)
            return 100.0 if val >= 0.5 else 0.0
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def normalize_velocity(cls, velocity: float | int | None) -> float:
        """Normalize velocity (transactions in preceding 1h) to 0.0 - 100.0 scale.

        Baseline:
        velocity <= 1 -> 0.0
        velocity = 2  -> 35.0
        velocity = 3  -> 70.0
        velocity >= 4 -> 100.0
        If value is already > 10, treat as already scaled.
        """
        if velocity is None:
            return 0.0
        try:
            val = float(velocity)
            if math.isnan(val) or math.isinf(val) or val <= 1.0:
                return 0.0
            if val > 10.0:
                return round(cls.clamp_score(val), 2)
            scaled = (val - 1.0) * 35.0
            return round(cls.clamp_score(scaled), 2)
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def compute_weighted_score(
        cls,
        signals: RiskSignals,
        weights: dict[str, float] | None = None,
    ) -> float:
        """Calculate linear weighted multi-signal sum.

        Formula:
          raw_score =
              tx_anomaly * 0.35 +
              comm_risk  * 0.30 +
              beh_dev    * 0.15 +
              new_payee  * 0.08 +
              velocity   * 0.07 +
              temp_corr  * 0.05
        """
        w_tx = weights.get("tx", RiskFusionConfig.WEIGHT_TRANSACTION_ANOMALY) if weights else RiskFusionConfig.WEIGHT_TRANSACTION_ANOMALY
        w_comm = weights.get("comm", RiskFusionConfig.WEIGHT_COMMUNICATION_RISK) if weights else RiskFusionConfig.WEIGHT_COMMUNICATION_RISK
        w_beh = weights.get("beh", RiskFusionConfig.WEIGHT_BEHAVIORAL_DEVIATION) if weights else RiskFusionConfig.WEIGHT_BEHAVIORAL_DEVIATION
        w_payee = weights.get("payee", RiskFusionConfig.WEIGHT_NEW_PAYEE) if weights else RiskFusionConfig.WEIGHT_NEW_PAYEE
        w_vel = weights.get("vel", RiskFusionConfig.WEIGHT_VELOCITY) if weights else RiskFusionConfig.WEIGHT_VELOCITY
        w_temp = weights.get("temp", RiskFusionConfig.WEIGHT_TEMPORAL_CORRELATION) if weights else RiskFusionConfig.WEIGHT_TEMPORAL_CORRELATION

        raw_sum = (
            signals.transaction_anomaly_score * w_tx
            + signals.communication_risk_score * w_comm
            + signals.behavioral_deviation_score * w_beh
            + signals.new_payee_score * w_payee
            + signals.velocity_score * w_vel
            + signals.temporal_correlation_score * w_temp
        )

        return round(cls.clamp_score(raw_sum), 2)

    @classmethod
    def apply_cross_signal_boost(
        cls,
        signals: RiskSignals,
        weighted_score: float,
        delta_minutes: float | None = None,
    ) -> tuple[float, float]:
        """Apply controlled +10 point correlation boost if high comm + high tx occur within 2h.

        Conditions for boost:
        1. Communication risk score >= 60.0
        2. Transaction anomaly score >= 60.0
        3. Communication occurred within 120 minutes prior to transaction (0 <= delta <= 120)

        Returns:
            tuple of (final_risk_score, boost_applied)
        """
        qualifies = (
            signals.communication_risk_score >= RiskFusionConfig.CROSS_SIGNAL_MIN_COMM_RISK
            and signals.transaction_anomaly_score >= RiskFusionConfig.CROSS_SIGNAL_MIN_TX_ANOMALY
            and delta_minutes is not None
            and 0.0 <= delta_minutes <= RiskFusionConfig.COMMUNICATION_TRANSACTION_WINDOW_MINUTES
        )

        boost = RiskFusionConfig.CROSS_SIGNAL_BOOST if qualifies else 0.0
        final_score = cls.clamp_score(weighted_score + boost)

        return round(final_score, 2), boost
