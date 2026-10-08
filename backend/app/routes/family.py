"""UPI Guardian - Family / Caregiver Blueprint."""

from flask import Blueprint
from app.services.family_service import FamilyService
from app.utils.responses import json_response

family_bp = Blueprint("family", __name__)


@family_bp.route("/family/profile", methods=["GET"])
def get_family_profile():
    """Get elder profile and safety metrics.

    GET /api/family/profile
    """
    profile = FamilyService.get_profile()
    return json_response(profile, status_code=200)


@family_bp.route("/family/alerts/resolve", methods=["POST"])
def resolve_family_alerts():
    """Resolve active urgent family alerts.

    POST /api/family/alerts/resolve
    """
    result = FamilyService.resolve_alerts()
    return json_response(result, status_code=200)
