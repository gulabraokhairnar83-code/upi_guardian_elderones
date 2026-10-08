"""UPI Guardian - Fraud Alerts Blueprint."""

from flask import Blueprint, request
from app.services.alert_service import AlertService
from app.utils.errors import ValidationError
from app.utils.responses import json_response

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/alerts", methods=["GET"])
def list_alerts():
    """List fraud alerts with optional severity filter.

    GET /api/alerts?level=critical
    """
    level = request.args.get("level")
    alerts = AlertService.list_alerts(level=level)
    return json_response(alerts, status_code=200)


@alerts_bp.route("/alerts/<alert_id>/resolve", methods=["POST"])
def resolve_alert(alert_id: str):
    """Mark an alert as resolved.

    POST /api/alerts/<alert_id>/resolve
    """
    try:
        numeric_id = int(alert_id)
    except ValueError:
        raise ValidationError(f"Invalid alert ID format: '{alert_id}'. Must be an integer.")

    result = AlertService.resolve(numeric_id)
    return json_response(result, status_code=200)
