"""UPI Guardian - Health Check Blueprint."""

from flask import Blueprint
from app.db import check_db_connection
from app.utils.responses import json_response

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Service health check endpoint.

    GET /api/health
    """
    db_status = check_db_connection()
    return json_response(
        {
            "status": "healthy",
            "service": "upi-guardian-backend",
            "version": "1.0.0",
            "database": db_status,
        },
        status_code=200,
    )
