"""UPI Guardian - Caregiver Service."""

from datetime import datetime, timezone, timedelta
import secrets
import uuid
from app.db.repositories.caregiver_repository import CaregiverRepository
from app.db.seed_data import PRIMARY_USER_ID
from app.utils.errors import NotFoundError, ForbiddenError, ValidationError

_repo = CaregiverRepository()


class CaregiverService:
    """Business logic for elder-caregiver relationships."""

    @staticmethod
    def list_caregivers(current_user: dict) -> list[dict]:
        """List caregivers authorized for the current user."""
        user_id = current_user.get("user_id", PRIMARY_USER_ID)
        role = current_user.get("role", "ELDER")

        if role == "CAREGIVER":
            # Caregiver can view relationships where they are the designated caregiver
            cursor = _repo.collection.find({
                "$or": [
                    {"caregiver_user_id": user_id},
                    {"email": current_user.get("email", "").lower()},
                ],
                "is_active": True,
            }).sort("created_at", -1)
            return _repo.clean_docs(list(cursor))

        # Default ELDER role: only see own caregivers
        return _repo.list_caregivers(elder_user_id=user_id, is_active=True)

    @staticmethod
    def get_caregiver(caregiver_id: str, current_user: dict) -> dict:
        """Get single caregiver record ensuring ownership authorization."""
        caregiver = _repo.get_by_id(caregiver_id)
        if not caregiver:
            raise NotFoundError(f"Caregiver '{caregiver_id}' not found.")

        user_id = current_user.get("user_id", PRIMARY_USER_ID)
        role = current_user.get("role", "ELDER")

        # Ownership authorization check
        is_owner_elder = caregiver.get("elder_user_id") == user_id or caregiver.get("user_id") == user_id
        is_matching_caregiver = (
            caregiver.get("caregiver_user_id") == user_id or
            (caregiver.get("email") and caregiver.get("email").lower() == current_user.get("email", "").lower())
        )

        if not (is_owner_elder or is_matching_caregiver):
            raise ForbiddenError("You are not authorized to access this caregiver.")

        return caregiver

    @staticmethod
    def create_caregiver(data: dict, current_user: dict) -> dict:
        """Create new caregiver for current elder user."""
        elder_id = current_user.get("user_id", PRIMARY_USER_ID)

        # Generate unique caregiver ID
        cg_id = f"cg_{uuid.uuid4().hex[:10]}"
        verification_token = secrets.token_hex(4).upper()  # 8-char verification code
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

        record_data = {
            "caregiver_id": cg_id,
            "elder_user_id": elder_id,
            "user_id": elder_id,
            "caregiver_user_id": data.get("caregiver_user_id"),
            "name": data["name"],
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "relationship": data.get("relationship", "OTHER"),
            "status": "PENDING",
            "is_verified": False,
            "is_active": True,
            "verification_token": verification_token,
            "verification_expires_at": expires_at,
            "notification_preferences": data.get("notification_preferences", {}),
        }

        created = _repo.create_caregiver(record_data)
        return created

    @staticmethod
    def update_caregiver(caregiver_id: str, updates: dict, current_user: dict) -> dict:
        """Update caregiver record ensuring elder ownership."""
        caregiver = CaregiverService.get_caregiver(caregiver_id, current_user)
        user_id = current_user.get("user_id", PRIMARY_USER_ID)

        # Only the elder can update preferences and caregiver details
        if caregiver.get("elder_user_id") != user_id and caregiver.get("user_id") != user_id:
            raise ForbiddenError("Only the elder account owner can modify caregiver settings.")

        updated = _repo.update_caregiver(caregiver_id, updates)
        if not updated:
            raise NotFoundError(f"Caregiver '{caregiver_id}' not found.")
        return updated

    @staticmethod
    def delete_caregiver(caregiver_id: str, current_user: dict) -> dict:
        """Deactivate caregiver record ensuring elder ownership."""
        caregiver = CaregiverService.get_caregiver(caregiver_id, current_user)
        user_id = current_user.get("user_id", PRIMARY_USER_ID)

        if caregiver.get("elder_user_id") != user_id and caregiver.get("user_id") != user_id:
            raise ForbiddenError("Only the elder account owner can remove a caregiver.")

        success = _repo.delete_caregiver(caregiver_id)
        return {"success": success, "caregiver_id": caregiver_id, "message": "Caregiver deactivated."}

    @staticmethod
    def verify_caregiver(caregiver_id: str, token: str | None, current_user: dict) -> dict:
        """Verify caregiver via token or authorized elder confirmation."""
        caregiver = _repo.get_by_id(caregiver_id)
        if not caregiver:
            raise NotFoundError(f"Caregiver '{caregiver_id}' not found.")

        user_id = current_user.get("user_id", PRIMARY_USER_ID)
        is_owner_elder = caregiver.get("elder_user_id") == user_id or caregiver.get("user_id") == user_id

        # If token provided, validate token
        if token:
            stored_token = caregiver.get("verification_token")
            expires_at = caregiver.get("verification_expires_at")
            if not stored_token or token.strip().upper() != stored_token.upper():
                raise ValidationError("Invalid verification token.")
            if expires_at and datetime.fromisoformat(expires_at) < datetime.now(timezone.utc):
                raise ValidationError("Verification token has expired.")
        elif not is_owner_elder:
            raise ForbiddenError("Verification token required or elder authorization needed.")

        verified = _repo.verify_caregiver(caregiver_id)
        return verified or {}
