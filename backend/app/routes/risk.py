"""UPI Guardian - Risk Fusion Blueprint."""

from flask import Blueprint, request
from app.db.repositories.risk_event_repository import RiskEventRepository
from app.risk_fusion.inference import RiskFusionService
from app.schemas.validators import validate_risk_analyze
from app.utils.responses import json_response

risk_bp = Blueprint("risk", __name__)
_service = RiskFusionService()
_event_repo = RiskEventRepository()


@risk_bp.route("/risk/analyze", methods=["POST"])
def analyze_risk():
    """Analyze multi-signal composite risk for a transaction.

    POST /api/risk/analyze
    """
    raw_json = request.get_json(silent=True)
    validated_payload = validate_risk_analyze(raw_json)

    analysis = _service.analyze_transaction_risk(
        transaction_data=validated_payload,
        user_id=validated_payload.get("user_id"),
    )

    return json_response(
        {
            "success": True,
            "analysis": analysis,
        },
        status_code=200,
    )


@risk_bp.route("/risk/events", methods=["GET"])
def get_risk_events():
    """List recent multi-signal risk events.

    GET /api/risk/events?user_id=...&limit=20
    """
    user_id = request.args.get("user_id")
    limit_str = request.args.get("limit", "20")
    try:
        limit = min(100, max(1, int(limit_str)))
    except ValueError:
        limit = 20

    events = _event_repo.list_events(user_id=user_id, limit=limit)
    return json_response(
        {
            "success": True,
            "events": events,
            "count": len(events),
        },
        status_code=200,
    )
