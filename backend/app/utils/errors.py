"""UPI Guardian - Centralized Error Handling."""

import logging
from flask import jsonify

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 400, payload: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> dict:
        result = {"error": self.message, "status": self.status_code}
        if self.payload:
            result["details"] = self.payload
        return result


class ValidationError(AppError):
    """Raised when request input fails validation."""

    def __init__(self, message: str, payload: dict | None = None):
        super().__init__(message, status_code=400, payload=payload)


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ModelNotAvailableError(AppError):
    """Raised when the ML model artifact is missing or unavailable."""

    def __init__(self, message: str = "Machine learning anomaly detection model is not available."):
        super().__init__(message, status_code=503)


class UnauthorizedError(AppError):
    """Raised when authentication is required or token is invalid."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppError):
    """Raised when authenticated user is not authorized to access resource."""

    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, status_code=403)


class ConflictError(AppError):
    """Raised when resource already exists or conflict arises."""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)


def register_error_handlers(app):
    """Register centralized JSON error handlers with the Flask app."""

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(400)
    def handle_bad_request(error):
        message = getattr(error, "description", "Bad request syntax or invalid parameters")
        return jsonify({"error": message, "status": 400}), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        message = getattr(error, "description", "Endpoint or resource not found")
        return jsonify({"error": message, "status": 404}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"error": "HTTP method not allowed for this endpoint", "status": 405}), 405

    @app.errorhandler(500)
    def handle_server_error(error):
        logger.exception("Unhandled server error: %s", error)
        return jsonify({"error": "Internal server error", "status": 500}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        if isinstance(error, AppError):
            return jsonify(error.to_dict()), error.status_code
        logger.exception("Unhandled server exception: %s", error)
        return jsonify({"error": "Internal server error", "status": 500}), 500
