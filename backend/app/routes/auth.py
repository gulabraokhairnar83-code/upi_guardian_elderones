"""UPI Guardian - Authentication Blueprint."""

from flask import Blueprint, request, g
from app.services.auth_service import AuthService
from app.schemas.validators import validate_register, validate_login, validate_forgot_password
from app.utils.auth import jwt_required
from app.utils.rate_limiter import rate_limit
from app.utils.responses import json_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/register", methods=["POST"])
@rate_limit(limit=10, per_seconds=60, key_prefix="auth_register")
def register():
    """Register a new user account.

    POST /api/auth/register
    """
    data = request.get_json(silent=True)
    validated = validate_register(data)
    result = AuthService.register(validated)
    return json_response(result, status_code=201)


@auth_bp.route("/auth/login", methods=["POST"])
@rate_limit(limit=15, per_seconds=60, key_prefix="auth_login")
def login():
    """Authenticate existing user.

    POST /api/auth/login
    """
    data = request.get_json(silent=True)
    validated = validate_login(data)
    result = AuthService.login(validated)
    return json_response(result, status_code=200)


@auth_bp.route("/auth/forgot-password", methods=["POST"])
@rate_limit(limit=10, per_seconds=60, key_prefix="auth_forgot_password")
def forgot_password():
    """Request password reset instructions.

    POST /api/auth/forgot-password
    """
    data = request.get_json(silent=True)
    validated = validate_forgot_password(data)
    result = AuthService.forgot_password(validated)
    return json_response(result, status_code=200)


@auth_bp.route("/auth/refresh", methods=["POST"])
@rate_limit(limit=30, per_seconds=60, key_prefix="auth_refresh")
def refresh():
    """Refresh access token using refresh token.

    POST /api/auth/refresh
    """
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token") or request.headers.get("X-Refresh-Token")
    result = AuthService.refresh(refresh_token)
    return json_response(result, status_code=200)


@auth_bp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    """Revoke active JWT token.

    POST /api/auth/logout
    """
    result = AuthService.logout(g.current_user)
    return json_response(result, status_code=200)


@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def get_me():
    """Retrieve currently authenticated user.

    GET /api/auth/me
    """
    result = AuthService.get_me(g.current_user["user_id"])
    return json_response(result, status_code=200)
