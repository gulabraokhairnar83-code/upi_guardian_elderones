"""UPI Guardian - Risk Fusion Explainability Engine.

Produces elder-friendly, transparent explanations, factor rankings,
and actionable guidance without exposing complex internal models.
"""

from app.risk_fusion.config import RiskFusionConfig
from app.risk_fusion.models import RiskSignals


class RiskFusionExplainer:
    """Translates composite multi-signal risk evaluations into elder-friendly plain text."""

    @classmethod
    def get_top_contributing_factors(
        cls,
        signals: RiskSignals,
        correlation_boost: float = 0.0,
        unusual_time: bool = False,
    ) -> list[str]:
        """Rank and return plain-English top contributing factors."""
        factors: list[tuple[float, str]] = []

        # 1. Temporal correlation / close proximity
        if signals.temporal_correlation_score >= 35.0 or correlation_boost > 0.0:
            factors.append((
                signals.temporal_correlation_score + (15.0 if correlation_boost > 0 else 0),
                "Transaction occurred shortly after suspicious communication",
            ))

        # 2. Suspicious communication
        if signals.communication_risk_score >= 50.0:
            factors.append((
                signals.communication_risk_score,
                "Suspicious communication detected",
            ))

        # 3. Transaction anomaly / amount deviation
        if signals.transaction_anomaly_score >= 60.0 or signals.behavioral_deviation_score >= 50.0:
            factors.append((
                max(signals.transaction_anomaly_score, signals.behavioral_deviation_score),
                "Unusual transaction amount",
            ))

        # 4. New Payee
        if signals.new_payee_score >= 50.0:
            factors.append((
                signals.new_payee_score,
                "New or unfamiliar payee",
            ))

        # 5. Velocity
        if signals.velocity_score >= 40.0:
            factors.append((
                signals.velocity_score,
                "Unusual payment frequency",
            ))

        # 6. Behavioral Deviation
        if signals.behavioral_deviation_score >= 60.0:
            factors.append((
                signals.behavioral_deviation_score,
                "Significant behavioral deviation from historical patterns",
            ))

        # 7. Unusual Hour
        if unusual_time:
            factors.append((
                45.0,
                "Transaction initiated at an unusual hour",
            ))

        # Sort factors by impact descending
        factors.sort(key=lambda item: item[0], reverse=True)

        factor_names = [f[1] for f in factors]
        if not factor_names:
            return ["Transaction aligns with normal baseline behavior"]
        return factor_names

    @classmethod
    def generate_explanation(
        cls,
        risk_level: str,
        top_factors: list[str],
        signals: RiskSignals,
        correlation_boost: float = 0.0,
    ) -> str:
        """Synthesize an understandable, cautious explanation.

        Never asserts confirmed fraud; always adheres to risk assessment phrasing.
        """
        level = (risk_level or "LOW").upper()

        if level == "CRITICAL":
            if correlation_boost > 0.0 or signals.temporal_correlation_score >= 40.0:
                return (
                    "High-risk activity detected because an unusual transaction occurred shortly "
                    "after a suspicious communication. The transaction involves significant "
                    "deviations from your normal pattern."
                )
            return (
                "High-risk activity detected due to multiple compounding anomalies, including "
                "extreme behavioral deviation and an unfamiliar payee."
            )

        if level == "HIGH":
            if signals.communication_risk_score >= 60.0 and signals.transaction_anomaly_score >= 50.0:
                return (
                    "Suspicious activity detected. A questionable communication was detected alongside "
                    "an unusual transaction attempt. We strongly recommend pausing to verify."
                )
            if signals.transaction_anomaly_score >= 60.0:
                return (
                    "Suspicious activity detected. This payment amount or recipient is highly atypical "
                    "compared to your standard banking history."
                )
            return (
                "Potential scam detected. Recent messages or payment indicators indicate elevated "
                "risk that warrants independent verification."
            )

        if level == "MEDIUM":
            if signals.communication_risk_score >= 50.0:
                return (
                    "Moderate risk detected due to a recent suspicious message. Please double-check "
                    "the recipient details before authorizing."
                )
            return (
                "Moderate risk detected. Some aspects of this payment differ slightly from your "
                "usual transaction history."
            )

        return (
            "Low risk. This payment aligns well with your usual habits, and no suspicious "
            "communication patterns were detected."
        )

    @classmethod
    def explain(
        cls,
        signals: RiskSignals,
        risk_level: str,
        correlation_boost: float = 0.0,
        unusual_time: bool = False,
    ) -> dict[str, Any]:
        """Generate complete explainability packet."""
        top_factors = cls.get_top_contributing_factors(
            signals=signals,
            correlation_boost=correlation_boost,
            unusual_time=unusual_time,
        )
        explanation = cls.generate_explanation(
            risk_level=risk_level,
            top_factors=top_factors,
            signals=signals,
            correlation_boost=correlation_boost,
        )
        action = RiskFusionConfig.get_action_for_level(risk_level)

        return {
            "top_contributing_factors": top_factors,
            "explanation": explanation,
            "recommended_action": action,
        }
