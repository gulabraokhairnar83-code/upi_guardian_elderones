import logging
from flask import Blueprint, request, g
from app.notifications.notification_repository import NotificationRepository
from app.notifications.escalation_service import EscalationService
from app.schemas.validators import validate_twilio_webhook
from app.utils.auth import jwt_required
from app.utils.rate_limiter import rate_limit
from app.utils.errors import NotFoundError, ForbiddenError
from app.utils.responses import json_response
from app.db.seed_data import PRIMARY_USER_ID

logger = logging.getLogger("upi_guardian.notifications")
notifications_bp = Blueprint("notifications", __name__)
_repo = NotificationRepository()


@notifications_bp.route("/notifications", methods=["GET"])
@jwt_required()
def list_notifications():
    """List notifications for current user or caregiver.

    GET /api/notifications
    """
    user_id = g.current_user.get("user_id", PRIMARY_USER_ID)
    limit = int(request.args.get("limit", 50))
    records = _repo.list_by_user(user_id=user_id, limit=limit)
    return json_response(records, status_code=200)


@notifications_bp.route("/notifications/<notification_id>", methods=["GET"])
@jwt_required()
def get_notification(notification_id: str):
    """Retrieve single notification record.

    GET /api/notifications/<notification_id>
    """
    record = _repo.get_by_id(notification_id)
    if not record:
        raise NotFoundError(f"Notification '{notification_id}' not found.")
    return json_response(record, status_code=200)


@notifications_bp.route("/notifications/<notification_id>/acknowledge", methods=["POST"])
@jwt_required()
def acknowledge_notification(notification_id: str):
    """Acknowledge an emergency or risk alert.

    POST /api/notifications/<notification_id>/acknowledge
    """
    record = _repo.get_by_id(notification_id)
    if not record:
        raise NotFoundError(f"Notification '{notification_id}' not found.")

    user_id = g.current_user.get("user_id", PRIMARY_USER_ID)
    # Check authorization: user must be associated with this notification
    is_authorized = (
        record.get("user_id") == user_id or
        record.get("elder_user_id") == user_id or
        record.get("caregiver_id") == user_id or
        record.get("caregiver_user_id") == user_id or
        g.current_user.get("role") == "CAREGIVER"
    )
    if not is_authorized:
        raise ForbiddenError("You are not authorized to acknowledge this notification.")

    updated = _repo.acknowledge_notification(notification_id, acknowledged_by=user_id)
    return json_response(updated, status_code=200)


@notifications_bp.route("/notifications/escalate", methods=["POST"])
@jwt_required()
@rate_limit(limit=20, per_seconds=60, key_prefix="notif_escalate")
def trigger_escalation():
    """Manually test or trigger risk escalation based on provided risk payload.

    POST /api/notifications/escalate
    """
    data = request.get_json(silent=True) or {}
    user_id = g.current_user.get("user_id", PRIMARY_USER_ID)
    result = EscalationService.escalate_risk_event(data, user_id=user_id)
    return json_response(result, status_code=200)


@notifications_bp.route("/notifications/webhook", methods=["POST"])
def twilio_webhook():
    """Provider delivery status receipt webhook.

    Receives delivery status updates (sent, delivered, failed, undelivered).
    Validates payload structure and updates notification repository safely.

    POST /api/notifications/webhook
    """
    # Accept either JSON or URL-encoded form data (standard Twilio callback)
    payload = request.get_json(silent=True) or (request.form.to_dict() if request.form else {})
    validated = validate_twilio_webhook(payload)

    sid = validated["provider_message_id"]
    status = validated["status"]
    err = validated.get("error")

    # Safe structured logging: only log metadata, never phone numbers or credentials
    logger.info("Delivery status receipt received for SID: %s, Status: %s", sid, status)

    updated = _repo.update_delivery_status(sid, status, err)
    return json_response(
        {
            "success": True,
            "message": "Webhook processed safely.",
            "provider_message_id": sid,
            "status": status,
            "updated": updated is not None,
        },
        status_code=200,
    )
