"""UPI Guardian - Settings Blueprint."""

from flask import Blueprint, request
from app.services.settings_service import SettingsService
from app.schemas.validators import validate_settings_patch
from app.utils.responses import json_response

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings", methods=["GET"])
def get_settings():
    """Retrieve user settings.

    GET /api/settings
    """
    settings = SettingsService.get_settings()
    return json_response(settings, status_code=200)


@settings_bp.route("/settings", methods=["PATCH"])
def update_settings():
    """Partially update user settings.

    PATCH /api/settings
    """
    data = request.get_json(silent=True)
    validated = validate_settings_patch(data)
    updated = SettingsService.update_settings(validated)
    return json_response(updated, status_code=200)
