"""UPI Guardian - Authentication & JWT Utilities.

Provides password hashing, JWT generation, validation, revocation checks,
and request authentication decorators.
"""

from datetime import datetime, timezone, timedelta
from functools import wraps
import uuid
import jwt
from flask import request, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from app.db.connection import get_db
from app.utils.errors import UnauthorizedError, ForbiddenError


def hash_password(password: str) -> str:
    """Generate secure salted hash for password."""
    return generate_password_hash(password, method="scrypt")


def verify_password(password: str, hashed: str) -> bool:
    """Verify plaintext password against stored hash."""
    if not password or not hashed:
        return False
    return check_password_hash(hashed, password)


def get_jwt_secret() -> str:
    """Retrieve active JWT secret key from application config."""
    return current_app.config.get("JWT_SECRET_KEY", "dev-jwt-secret-key-change-in-production")


def create_access_token(
    user_id: str,
    role: str,
    email: str,
    expires_in_seconds: int | None = None,
    extra_claims: dict | None = None,
) -> str:
    """Create a signed short-lived JWT access token."""
    if expires_in_seconds is None:
        expires_in_seconds = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600)

    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "role": role.upper(),
        "email": email.lower(),
        "jti": jti,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, get_jwt_secret(), algorithm="HS256")


def create_refresh_token(
    user_id: str,
    expires_in_seconds: int | None = None,
) -> str:
    """Create a signed long-lived JWT refresh token."""
    if expires_in_seconds is None:
        expires_in_seconds = current_app.config.get("JWT_REFRESH_TOKEN_EXPIRES", 604800)

    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "jti": jti,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm="HS256")


def decode_token(token: str) -> dict:
    """Decode and validate JWT token signature and expiration."""
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError as err:
        raise UnauthorizedError("Authentication token has expired. Please log in again.") from err
    except (jwt.InvalidTokenError, jwt.DecodeError, Exception) as err:
        raise UnauthorizedError("Invalid authentication token.") from err


def is_token_revoked(jti: str) -> bool:
    """Check if token JTI has been revoked in MongoDB."""
    if not jti:
        return False
    db = get_db()
    doc = db.revoked_tokens.find_one({"jti": jti})
    return doc is not None


def revoke_token(jti: str, exp_timestamp: int) -> None:
    """Record token JTI into revoked_tokens collection with TTL auto-cleanup."""
    if not jti:
        return
    db = get_db()
    # Store BSON UTC datetime so MongoDB TTL index automatically purges expired records
    exp_dt = datetime.fromtimestamp(exp_timestamp, timezone.utc)
    db.revoked_tokens.update_one(
        {"jti": jti},
        {
            "$set": {
                "jti": jti,
                "revoked_at": datetime.now(timezone.utc),
                "expires_at": exp_dt,
            }
        },
        upsert=True,
    )


def extract_token_from_request() -> str | None:
    """Extract Bearer token from Authorization header or cookie."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    # Check query param (e.g. for dev/download links) or cookie fallback
    token_cookie = request.cookies.get("access_token")
    if token_cookie:
        return token_cookie.strip()
    return None


def jwt_required(optional: bool = False):
    """Decorator requiring a valid JWT access token on protected endpoints."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = extract_token_from_request()
            if not token:
                if optional:
                    g.current_user = None
                    return fn(*args, **kwargs)
                raise UnauthorizedError("Missing authentication token. Authorization header required.")

            payload = decode_token(token)
            if payload.get("type") != "access":
                raise UnauthorizedError("Invalid token type. Access token expected.")

            if is_token_revoked(payload.get("jti", "")):
                raise UnauthorizedError("Authentication token has been revoked. Please log in again.")

            user_id = payload.get("user_id")
            # Verify user account is not deactivated
            from app.db.repositories.user_repository import UserRepository
            user = UserRepository().get_by_id(user_id)
            if user and not user.get("is_active", True):
                raise UnauthorizedError("User account has been deactivated.")

            g.current_user = {
                "user_id": user_id,
                "role": payload.get("role", "ELDER").upper(),
                "email": payload.get("email"),
                "jti": payload.get("jti"),
                "exp": payload.get("exp"),
            }
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def roles_required(*allowed_roles: str):
    """Decorator ensuring current authenticated user has an allowed role."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not getattr(g, "current_user", None):
                raise UnauthorizedError("Authentication required.")
            user_role = g.current_user.get("role", "").upper()
            allowed_upper = [r.upper() for r in allowed_roles]
            if user_role not in allowed_upper:
                raise ForbiddenError(
                    f"Access forbidden: User role '{user_role}' is not authorized for this resource."
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
