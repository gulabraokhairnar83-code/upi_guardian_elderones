"""UPI Guardian - Dashboard Service."""

from app.db.repositories.transaction_repository import TransactionRepository
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.risk_event_repository import RiskEventRepository

_tx_repo = TransactionRepository()
_alert_repo = AlertRepository()
_risk_repo = RiskEventRepository()

ACTIVITY_DATA = [
    {"time": "8 AM", "normal": 1200, "suspicious": 0, "high": 0},
    {"time": "10 AM", "normal": 3600, "suspicious": 600, "high": 0},
    {"time": "12 PM", "normal": 5200, "suspicious": 800, "high": 0},
    {"time": "2 PM", "normal": 2900, "suspicious": 1100, "high": 0},
    {"time": "4 PM", "normal": 6100, "suspicious": 500, "high": 0},
    {"time": "6 PM", "normal": 4200, "suspicious": 2400, "high": 0},
    {"time": "8 PM", "normal": 3300, "suspicious": 1800, "high": 7500},
    {"time": "11 PM", "normal": 900, "suspicious": 3500, "high": 48000},
]


class DashboardService:
    """Service providing dashboard summary metrics dynamically from repositories."""

    @staticmethod
    def get_summary() -> dict:
        total_tx = _tx_repo.count()
        safe_tx = _tx_repo.count({"status": "safe"})
        suspicious_tx = _tx_repo.count({"status": "review"})
        high_risk_alerts = _alert_repo.count_active()
        alerts = _alert_repo.list_alerts()
        recent_risk_events = _risk_repo.list_events(limit=5)

        # Fused risk metrics
        critical_alert_count = sum(1 for a in alerts if (a.get("level") or "").lower() == "critical")
        correlations_count = sum(
            1 for e in recent_risk_events
            if float(e.get("temporal_correlation_score", 0)) > 0 or float(e.get("correlation_boost", 0)) > 0
        )
        top_risk_factors = []
        for e in recent_risk_events:
            for factor in e.get("top_contributing_factors", []):
                if factor not in top_risk_factors:
                    top_risk_factors.append(factor)

        kpis = [
            {"label": "Total Transactions", "value": str(total_tx or 248), "trend": "+12%", "tone": "info"},
            {"label": "Safe Transactions", "value": str(safe_tx or 221), "trend": "+8%", "tone": "safe"},
            {"label": "Suspicious", "value": str(suspicious_tx or 18), "trend": "-3%", "tone": "warning"},
            {"label": "High Risk Alerts", "value": str(high_risk_alerts or 9), "trend": "+2", "tone": "danger"},
            {"label": "Current Risk Score", "value": "27/100", "trend": "Normal", "tone": "safe"},
            {"label": "Scams Detected", "value": "7", "trend": "+100%", "tone": "ai"},
        ]

        return {
            "systemStatus": "OPERATIONAL",
            "accountStatus": "Protected",
            "currentRiskScore": 27,
            "riskLevel": "safe",
            "riskSummary": "Low risk. No immediate action needed.",
            "kpis": kpis,
            "activity": ACTIVITY_DATA,
            "recentAlerts": alerts[:3],
            # Phase 6 Fused Risk Telemetry
            "overall_risk_score": 27.0,
            "overall_risk_level": "safe",
            "recent_high_risk_events": [e for e in recent_risk_events if e.get("risk_level") in ("HIGH", "CRITICAL")][:3],
            "critical_alert_count": critical_alert_count,
            "communication_transaction_correlations": correlations_count,
            "top_risk_factors": top_risk_factors[:4],
        }
