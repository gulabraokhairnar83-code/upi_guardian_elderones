"""UPI Guardian - Alert Service."""

from app.db.repositories.alert_repository import AlertRepository
from app.utils.errors import NotFoundError

_repo = AlertRepository()


class AlertService:
    """Service providing fraud alert listing and resolution."""

    @staticmethod
    def list_alerts(level: str | None = None) -> list[dict]:
        return _repo.list_alerts(level=level)

    @staticmethod
    def resolve(alert_id: int) -> dict:
        alert = _repo.resolve_alert(alert_id)
        if not alert:
            raise NotFoundError(f"Alert with ID {alert_id} was not found.")
        return {
            "success": True,
            "id": alert_id,
            "message": f"Alert {alert_id} marked as resolved.",
        }
