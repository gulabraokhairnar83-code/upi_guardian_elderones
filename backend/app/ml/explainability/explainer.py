"""UPI Guardian - Behavioral Explainability Layer.

Translates transaction features and historical context into human-interpretable
risk factors for elderly users and their designated caregivers.

NOTE: Isolation Forest is an unsupervised tree ensemble that isolates data points,
and does not provide native feature importance weights for individual samples.
Therefore, this explainability layer derives contributing factors through
domain-specific behavioral comparison rules against the user's historical profile.
It clearly distinguishes ML anomaly predictions from behavioral heuristics.
"""


class BehavioralExplainer:
    """Generates explainable factor breakdowns and recommendations from behavioral signals."""

    @classmethod
    def explain(
        cls,
        features: dict[str, float],
        anomaly_score: float,
        risk_level: str,
        historical_stats: dict | None = None,
    ) -> dict:
        """Analyze extracted features and produce human-readable contributing factors.

        Args:
            features: Dictionary containing 'amount', 'z_score_deviation', 'velocity',
                      'is_new_payee', 'unusual_time'.
            anomaly_score: ML model's normalized 0-100 anomaly score.
            risk_level: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'.
            historical_stats: Optional user historical context (mean, std, known_payees).

        Returns:
            dict containing:
                - 'contributing_factors': list of structured factor objects
                - 'explanation': summary sentence
                - 'recommended_action': 'allow' | 'review' | 'block'
        """
        factors = []
        stats = historical_stats or {}
        mean = stats.get("mean", 0.0)

        amount = features.get("amount", 0.0)
        z_score = features.get("z_score_deviation", 0.0)
        velocity = features.get("velocity", 1.0)
        is_new_payee = bool(features.get("is_new_payee", 0.0))
        unusual_time = bool(features.get("unusual_time", 0.0))

        # 1. Amount Deviation Factor
        if z_score >= 3.0 or (mean > 0 and amount >= mean * 4.0):
            factors.append({
                "factor": "amount_deviation",
                "value": round(amount, 2),
                "severity": "CRITICAL" if z_score >= 4.5 else "HIGH",
                "message": (
                    f"Transaction amount of ₹{amount:,.2f} is exceptionally higher than the user's "
                    f"historical average of ₹{mean:,.2f} (z-score: {z_score:.2f})."
                    if mean > 0
                    else f"Transaction amount of ₹{amount:,.2f} represents an unusually large outbound transfer."
                ),
            })
        elif z_score >= 1.75 or (mean > 0 and amount >= mean * 2.0):
            factors.append({
                "factor": "amount_deviation",
                "value": round(amount, 2),
                "severity": "MEDIUM",
                "message": (
                    f"Transaction amount of ₹{amount:,.2f} moderately exceeds routine spending habits "
                    f"(average: ₹{mean:,.2f})."
                    if mean > 0
                    else f"Transaction amount of ₹{amount:,.2f} is moderately elevated."
                ),
            })

        # 2. New Payee Factor
        if is_new_payee:
            factors.append({
                "factor": "new_payee",
                "value": 1,
                "severity": "HIGH" if (amount > 10000 or unusual_time) else "MEDIUM",
                "message": "Payment recipient has never been transacted with previously by this account.",
            })

        # 3. Velocity Factor
        if velocity >= 4:
            factors.append({
                "factor": "velocity",
                "value": int(velocity),
                "severity": "CRITICAL" if velocity >= 6 else "HIGH",
                "message": f"High frequency spike detected: {int(velocity)} transactions attempted within 1 hour.",
            })
        elif velocity >= 3:
            factors.append({
                "factor": "velocity",
                "value": int(velocity),
                "severity": "MEDIUM",
                "message": f"Elevated frequency: {int(velocity)} transactions in the past hour.",
            })

        # 4. Unusual Time Factor
        if unusual_time:
            factors.append({
                "factor": "unusual_time",
                "value": 1,
                "severity": "HIGH" if (is_new_payee or amount > 5000) else "MEDIUM",
                "message": "Transaction initiated during late night / early morning hours (11:00 PM – 5:00 AM).",
            })

        # 5. Behavioral Deviation (Multi-Signal Compound Factor)
        if len(factors) >= 2 and anomaly_score >= 60.0:
            factors.append({
                "factor": "behavioral_deviation",
                "value": round(anomaly_score, 1),
                "severity": "CRITICAL" if anomaly_score >= 85.0 else "HIGH",
                "message": "Multiple compounding risk signals diverge sharply from the elder user's baseline behavior.",
            })

        # Overall summary explanation
        explanation = cls._generate_summary_explanation(factors, risk_level, anomaly_score)

        # Recommended action mapping
        if risk_level == "CRITICAL":
            recommended_action = "block"
        elif risk_level in ("HIGH", "MEDIUM"):
            recommended_action = "review"
        else:
            recommended_action = "allow"

        return {
            "contributing_factors": factors,
            "explanation": explanation,
            "recommended_action": recommended_action,
        }

    @staticmethod
    def _generate_summary_explanation(
        factors: list[dict],
        risk_level: str,
        anomaly_score: float,
    ) -> str:
        """Synthesize factors into a clear, concise explanation."""
        if not factors:
            return (
                f"Transaction matches regular behavioral baseline with a low anomaly score of {anomaly_score:.1f}. "
                "No suspicious behavioral patterns detected."
            )

        factor_names = [f["factor"].replace("_", " ") for f in factors if f["factor"] != "behavioral_deviation"]
        joined_names = ", ".join(factor_names)

        if risk_level == "CRITICAL":
            return (
                f"Critical anomaly detected (score {anomaly_score:.1f}/100). "
                f"Immediate safety review warranted due to suspicious {joined_names}."
            )
        if risk_level == "HIGH":
            return (
                f"Elevated transaction anomaly detected (score {anomaly_score:.1f}/100) "
                f"driven by {joined_names}."
            )
        if risk_level == "MEDIUM":
            return (
                f"Moderate behavioral deviation (score {anomaly_score:.1f}/100). "
                f"Notable factors: {joined_names}."
            )
        return (
            f"Transaction is within acceptable variance (score {anomaly_score:.1f}/100). "
            f"Observed: {joined_names}."
        )
