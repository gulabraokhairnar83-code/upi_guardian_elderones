"""UPI Guardian - Flask Application Factory."""

import logging
import os
from flask import Flask, request
from app.config import config_by_name
from app.extensions import cors
from app.db import init_db
from app.utils.errors import register_error_handlers
from app.routes import register_blueprints


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure an instance of the Flask application."""
    if not config_name:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # Configure logging
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    )
    app.logger.setLevel(log_level)

    # Initialize extensions
    cors_origins = app.config.get("CORS_ORIGINS") or [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        supports_credentials=True,
    )

    # Security Headers Hook (WCAG / OWASP compliance)
    @app.after_request
    def apply_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        if app.config.get("ENABLE_HSTS", False) or (config_name == "production" and request.is_secure):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # Initialize database connection & collection indexes
    init_db(app)

    # Register error handlers
    register_error_handlers(app)

    # Register modular blueprints
    register_blueprints(app)

    app.logger.info("UPI Guardian Flask API initialized with config: %s", config_name)
    return app
