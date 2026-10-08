"""UPI Guardian - Settings Service."""

from app.db.repositories.settings_repository import SettingsRepository

_repo = SettingsRepository()


class SettingsService:
    """Service providing user settings read and partial update."""

    @staticmethod
    def get_settings() -> dict:
        return _repo.get_settings()

    @staticmethod
    def update_settings(updates: dict) -> dict:
        return _repo.update_settings(updates)
