"""UPI Guardian - Blueprint Registration."""

from flask import Flask
from .health import health_bp
from .dashboard import dashboard_bp
from .transactions import transactions_bp
from .alerts import alerts_bp
from .family import family_bp
from .messages import messages_bp
from .settings import settings_bp
from .risk import risk_bp
from .auth import auth_bp
from .caregivers import caregivers_bp
from .notifications import notifications_bp


def register_blueprints(app: Flask):
    """Register all modular application blueprints under /api."""
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(transactions_bp, url_prefix="/api")
    app.register_blueprint(alerts_bp, url_prefix="/api")
    app.register_blueprint(family_bp, url_prefix="/api")
    app.register_blueprint(messages_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api")
    app.register_blueprint(risk_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(caregivers_bp, url_prefix="/api")
    app.register_blueprint(notifications_bp, url_prefix="/api")
