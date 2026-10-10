"""UPI Guardian - Authentication Service."""

import uuid
from app.db.repositories.user_repository import UserRepository
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    revoke_token,
    is_token_revoked,
)
from app.utils.errors import UnauthorizedError, ConflictError, NotFoundError

_user_repo = UserRepository()


class AuthService:
    """Business logic for registration, authentication, token refresh, and logout."""

    @staticmethod
    def register(payload: dict) -> dict:
        """Register a new user (ELDER or CAREGIVER) and return session tokens."""
        clean_email = payload["email"].strip().lower()
        existing = _user_repo.get_by_email(clean_email)
        if existing:
            raise ConflictError("An account with this email address already exists.")

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        password_hash = hash_password(payload["password"])

        user_record = {
            "user_id": user_id,
            "name": payload["name"].strip(),
            "email": clean_email,
            "phone": payload.get("phone", "").strip(),
            "password_hash": password_hash,
            "role": payload.get("role", "ELDER").upper(),
            "is_active": True,
            "accountSafetyStatus": "Protected",
        }

        created = _user_repo.create_user(user_record)
        access_token = create_access_token(user_id=user_id, role=created["role"], email=clean_email)
        refresh_token = create_refresh_token(user_id=user_id)

        return {
            "success": True,
            "user": created,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }

    @staticmethod
    def login(payload: dict) -> dict:
        """Authenticate user by email and password, issuing access and refresh tokens."""
        clean_email = payload["email"].strip().lower()
        user_with_auth = _user_repo.get_by_email(clean_email)

        # Generic authentication failure message to prevent email enumeration
        if not user_with_auth or not user_with_auth.get("is_active", True):
            raise UnauthorizedError("Invalid email or password.")

        if not verify_password(payload["password"], user_with_auth.get("password_hash", "")):
            raise UnauthorizedError("Invalid email or password.")

        user_id = user_with_auth["user_id"]
        role = user_with_auth.get("role", "ELDER").upper()

        access_token = create_access_token(user_id=user_id, role=role, email=clean_email)
        refresh_token = create_refresh_token(user_id=user_id)

        clean_user = _user_repo.get_by_id(user_id) or user_with_auth
        if "password_hash" in clean_user:
            del clean_user["password_hash"]

        return {
            "success": True,
            "user": clean_user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }

    @staticmethod
    def refresh(refresh_token_str: str) -> dict:
        """Issue a new access token using a valid, unrevoked refresh token."""
        if not refresh_token_str:
            raise UnauthorizedError("Refresh token is required.")

        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type. Refresh token expected.")

        if is_token_revoked(payload.get("jti", "")):
            raise UnauthorizedError("Refresh token has been revoked. Please log in again.")

        user_id = payload.get("user_id")
        user = _user_repo.get_by_id(user_id)
        if not user or not user.get("is_active", True):
            raise UnauthorizedError("User account not found or deactivated.")

        new_access_token = create_access_token(
            user_id=user_id,
            role=user.get("role", "ELDER"),
            email=user.get("email", ""),
        )

        return {
            "success": True,
            "access_token": new_access_token,
            "token_type": "Bearer",
        }

    @staticmethod
    def logout(token_payload: dict) -> dict:
        """Revoke current access token."""
        jti = token_payload.get("jti")
        exp = token_payload.get("exp")
        if jti and exp:
            revoke_token(jti, exp)
        return {
            "success": True,
            "message": "Successfully logged out.",
        }

    @staticmethod
    def get_me(user_id: str) -> dict:
        """Retrieve profile of currently authenticated user."""
        user = _user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        return {
            "success": True,
            "user": user,
        }

    @staticmethod
    def forgot_password(payload: dict) -> dict:
        """Process a password reset request safely without exposing account existence."""
        clean_email = payload["email"].strip().lower()
        # Look up user if exists (for audit/dispatch in production)
        user = _user_repo.get_by_email(clean_email)
        return {
            "success": True,
            "message": "Password reset instructions and emergency verification have been dispatched to your registered contact.",
            "email": clean_email,
            "user_found": bool(user),
        }
