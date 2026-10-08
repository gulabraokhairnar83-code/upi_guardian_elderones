"""UPI Guardian - Dashboard Blueprint."""

from flask import Blueprint
from app.services.dashboard_service import DashboardService
from app.utils.responses import json_response

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def get_dashboard_summary():
    """Get dashboard telemetry summary.

    GET /api/dashboard/summary
    """
    summary = DashboardService.get_summary()
    return json_response(summary, status_code=200)
