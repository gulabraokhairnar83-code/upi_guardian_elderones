"""UPI Guardian - Message / Communication Analysis Blueprint."""

from flask import Blueprint, request
from app.services.message_service import MessageService
from app.schemas.validators import validate_analyze_message
from app.utils.responses import json_response

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/analyze-message", methods=["POST"])
def analyze_message():
    """Analyze an SMS or call transcript for fraud, phishing, or coercion patterns.

    POST /api/analyze-message
    """
    data = request.get_json(silent=True)
    validated = validate_analyze_message(data)
    result = MessageService.analyze_message(validated)
    return json_response(result, status_code=200)
