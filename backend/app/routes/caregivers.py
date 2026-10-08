"""UPI Guardian - Caregiver Blueprint."""

from flask import Blueprint, request, g
from app.services.caregiver_service import CaregiverService
from app.schemas.validators import validate_caregiver_create, validate_caregiver_patch
from app.utils.auth import jwt_required
from app.utils.responses import json_response

caregivers_bp = Blueprint("caregivers", __name__)


@caregivers_bp.route("/caregivers", methods=["GET"])
@jwt_required()
def list_caregivers():
    """List caregivers associated with the authenticated user.

    GET /api/caregivers
    """
    caregivers = CaregiverService.list_caregivers(g.current_user)
    return json_response(caregivers, status_code=200)


@caregivers_bp.route("/caregivers", methods=["POST"])
@jwt_required()
def create_caregiver():
    """Create a new caregiver.

    POST /api/caregivers
    """
    data = request.get_json(silent=True)
    validated = validate_caregiver_create(data)
    result = CaregiverService.create_caregiver(validated, g.current_user)
    return json_response(result, status_code=201)


@caregivers_bp.route("/caregivers/<caregiver_id>", methods=["GET"])
@jwt_required()
def get_caregiver(caregiver_id: str):
    """Retrieve details for a specific caregiver.

    GET /api/caregivers/<caregiver_id>
    """
    result = CaregiverService.get_caregiver(caregiver_id, g.current_user)
    return json_response(result, status_code=200)


@caregivers_bp.route("/caregivers/<caregiver_id>", methods=["PATCH"])
@jwt_required()
def update_caregiver(caregiver_id: str):
    """Update caregiver details or notification preferences.

    PATCH /api/caregivers/<caregiver_id>
    """
    data = request.get_json(silent=True)
    validated = validate_caregiver_patch(data)
    result = CaregiverService.update_caregiver(caregiver_id, validated, g.current_user)
    return json_response(result, status_code=200)


@caregivers_bp.route("/caregivers/<caregiver_id>", methods=["DELETE"])
@jwt_required()
def delete_caregiver(caregiver_id: str):
    """Deactivate a caregiver relationship.

    DELETE /api/caregivers/<caregiver_id>
    """
    result = CaregiverService.delete_caregiver(caregiver_id, g.current_user)
    return json_response(result, status_code=200)


@caregivers_bp.route("/caregivers/<caregiver_id>/verify", methods=["POST"])
@jwt_required()
def verify_caregiver(caregiver_id: str):
    """Verify a caregiver relationship with optional verification token.

    POST /api/caregivers/<caregiver_id>/verify
    """
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    result = CaregiverService.verify_caregiver(caregiver_id, token, g.current_user)
    return json_response(result, status_code=200)
