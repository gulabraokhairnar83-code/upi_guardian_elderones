"""UPI Guardian - Flask Application Configuration."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    TESTING = False
    DEBUG = False

    # MongoDB Atlas settings
    MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "upi_guardian_dev").strip()
    USE_MOCK_DB = os.getenv("USE_MOCK_DB", "false").lower() in ("true", "1", "yes")

    # JWT authentication settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "604800"))

    # Twilio notification settings
    TWILIO_ENABLED = os.getenv("TWILIO_ENABLED", "false").lower() in ("true", "1", "yes")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    TWILIO_FROM_PHONE = os.getenv("TWILIO_FROM_PHONE", "").strip()

    # Security headers & rate limiting
    ENABLE_HSTS = os.getenv("ENABLE_HSTS", "false").lower() in ("true", "1", "yes")
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    LOG_LEVEL = "DEBUG"
    # In development, if MONGODB_URI is not set, use mock DB automatically
    USE_MOCK_DB = os.getenv("USE_MOCK_DB", "true").lower() in ("true", "1", "yes") if not os.getenv("MONGODB_URI") else False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    LOG_LEVEL = "WARNING"
    MONGODB_DATABASE = "upi_guardian_test"
    USE_MOCK_DB = True  # Always use mock DB for unit tests
    TWILIO_ENABLED = False
    RATE_LIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    LOG_LEVEL = "INFO"
    USE_MOCK_DB = False
    ENABLE_HSTS = os.getenv("ENABLE_HSTS", "true").lower() in ("true", "1", "yes")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
