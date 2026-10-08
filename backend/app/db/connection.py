"""UPI Guardian - MongoDB Atlas Connection & Lifecycle Management."""

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError
import mongomock

logger = logging.getLogger(__name__)

_mongo_client: MongoClient | None = None
_mongo_db = None
_is_mock_db: bool = False


def init_db(app):
    """Initialize database connection from Flask application config."""
    global _mongo_client, _mongo_db, _is_mock_db

    uri = app.config.get("MONGODB_URI", "")
    db_name = app.config.get("MONGODB_DATABASE", "upi_guardian_dev")
    use_mock = app.config.get("USE_MOCK_DB", False)

    if use_mock or not uri:
        logger.info("[Database] Initializing isolated development mock database (mongomock).")
        _mongo_client = mongomock.MongoClient()
        _mongo_db = _mongo_client[db_name]
        _is_mock_db = True
    else:
        try:
            logger.info("[Database] Connecting to MongoDB Atlas cluster...")
            _mongo_client = MongoClient(
                uri,
                serverSelectionTimeoutMS=4000,
                connectTimeoutMS=4000,
                appname="UPIGuardianBackend",
            )
            # Verify connectivity with ping command
            _mongo_client.admin.command("ping")
            _mongo_db = _mongo_client[db_name]
            _is_mock_db = False
            logger.info("[Database] Successfully connected to MongoDB Atlas database '%s'", db_name)
        except (ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError) as err:
            logger.warning(
                "[Database] MongoDB Atlas connection failed (%s). Falling back to development mock DB.",
                err,
            )
            if app.config.get("DEBUG") or app.config.get("TESTING"):
                _mongo_client = mongomock.MongoClient()
                _mongo_db = _mongo_client[db_name]
                _is_mock_db = True
            else:
                raise

    create_indexes()
    from app.db.seed_data import seed_initial_data
    seed_initial_data(_mongo_db)


def get_db():
    """Return the active MongoDB database instance."""
    global _mongo_db
    if _mongo_db is None:
        # Fallback safeguard
        logger.warning("[Database] get_db() called before init_db(). Creating default mock instance.")
        _client = mongomock.MongoClient()
        _mongo_db = _client["upi_guardian_dev"]
    return _mongo_db


def is_mock_active() -> bool:
    """Return True if currently operating on an in-memory mock database."""
    return _is_mock_db


def check_db_connection() -> dict:
    """Health check helper returning database status."""
    global _mongo_client, _is_mock_db
    if _mongo_client is None:
        return {"connected": False, "status": "uninitialized"}

    try:
        if not _is_mock_db:
            _mongo_client.admin.command("ping")
        return {
            "connected": True,
            "engine": "mongomock" if _is_mock_db else "MongoDB Atlas",
            "status": "healthy",
        }
    except Exception as err:
        logger.error("[Database] Health probe connection error: %s", err)
        return {"connected": False, "error": "Database service unavailable", "status": "unhealthy"}


def create_indexes():
    """Create appropriate indexes on all 7 application collections."""
    db = get_db()
    try:
        # 1. users
        db.users.create_index("user_id", unique=True, sparse=True)
        db.users.create_index("email", unique=True, sparse=True)
        db.users.create_index("phone", sparse=True)

        # 2. transactions
        db.transactions.create_index("id", unique=True)
        db.transactions.create_index("user_id")
        db.transactions.create_index([("user_id", 1), ("timestamp", -1)])
        db.transactions.create_index("status")
        db.transactions.create_index("payee")

        # 3. alerts
        db.alerts.create_index("id", unique=True)
        db.alerts.create_index("user_id")
        db.alerts.create_index("level")
        db.alerts.create_index("status")

        # 4. analyzed_messages
        db.analyzed_messages.create_index("user_id")
        db.analyzed_messages.create_index("analyzed_at")
        db.analyzed_messages.create_index("type")

        # 5. risk_events
        db.risk_events.create_index("user_id")
        db.risk_events.create_index("timestamp")

        # 6. caregivers
        db.caregivers.create_index("caregiver_id", unique=True, sparse=True)
        db.caregivers.create_index("elder_user_id")
        db.caregivers.create_index("caregiver_user_id")
        db.caregivers.create_index("user_id")
        db.caregivers.create_index("is_active")

        # 7. notification_preferences
        db.notification_preferences.create_index("user_id", unique=True)

        # 8. notifications (Phase 8)
        db.notifications.create_index("notification_id", unique=True, sparse=True)
        db.notifications.create_index("user_id")
        db.notifications.create_index("caregiver_id")
        db.notifications.create_index("risk_event_id")
        db.notifications.create_index("transaction_id")
        db.notifications.create_index("created_at")

        # 9. revoked_tokens (Phase 8/9 token blacklist with TTL auto-cleanup)
        db.revoked_tokens.create_index("jti", unique=True, sparse=True)
        db.revoked_tokens.create_index("expires_at", expireAfterSeconds=0)

        logger.info("[Database] Successfully verified all collection indexes.")
    except Exception as err:
        logger.warning("[Database] Index creation skipped or partially applied: %s", err)
