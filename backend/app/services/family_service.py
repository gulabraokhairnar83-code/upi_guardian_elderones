"""UPI Guardian - Family & Caregiver Service."""

from app.db.repositories.family_repository import FamilyRepository

_repo = FamilyRepository()


class FamilyService:
    """Service providing elder profile and caregiver controls."""

    @staticmethod
    def get_profile() -> dict:
        profile = _repo.get_elder_profile()
        return profile or {}

    @staticmethod
    def resolve_alerts() -> dict:
        profile = _repo.resolve_family_alerts()
        return {
            "success": True,
            "message": "All urgent family alerts have been marked as resolved.",
            "profile": profile,
        }
