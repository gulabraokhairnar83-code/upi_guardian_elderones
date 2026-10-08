"""UPI Guardian - In-Memory Sliding Window Rate Limiter.

Protects sensitive authentication, escalation, and analysis endpoints from abuse.
Designed for single-instance / development safety with clean integration for
production infrastructure-level rate limiting (e.g., NGINX, Cloudflare).
"""

import time
import threading
from functools import wraps
from flask import request, current_app, jsonify, g

_lock = threading.Lock()
_request_history: dict[str, list[float]] = {}


def reset_rate_limiter() -> None:
    """Clear in-memory request history (useful for automated testing)."""
    with _lock:
        _request_history.clear()


def get_client_identifier() -> str:
    """Derive client key based on authenticated user ID or real client IP."""
    if hasattr(g, "current_user") and g.current_user and "user_id" in g.current_user:
        return f"user:{g.current_user['user_id']}"

    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # First IP in X-Forwarded-For is client
        client_ip = forwarded_for.split(",")[0].strip()
        return f"ip:{client_ip}"

    return f"ip:{request.remote_addr or '127.0.0.1'}"


def rate_limit(limit: int = 10, per_seconds: int = 60, key_prefix: str = ""):
    """Decorator applying sliding-window rate limiting to Flask route functions.

    :param limit: Maximum allowed requests within the time window.
    :param per_seconds: Duration of sliding window in seconds.
    :param key_prefix: Distinct prefix for specific endpoints.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_app.config.get("RATE_LIMIT_ENABLED", True):
                return fn(*args, **kwargs)

            client_id = get_client_identifier()
            bucket_key = f"{key_prefix}:{client_id}" if key_prefix else client_id
            now = time.time()
            cutoff = now - per_seconds

            with _lock:
                timestamps = _request_history.get(bucket_key, [])
                # Prune timestamps older than window
                active_timestamps = [ts for ts in timestamps if ts > cutoff]

                if len(active_timestamps) >= limit:
                    oldest = active_timestamps[0]
                    retry_after = max(1, int(cutoff - oldest + per_seconds))
                    response = jsonify(
                        {
                            "error": "Rate limit exceeded. Please try again later.",
                            "status": 429,
                            "retry_after": retry_after,
                        }
                    )
                    response.status_code = 429
                    response.headers["Retry-After"] = str(retry_after)
                    return response

                active_timestamps.append(now)
                _request_history[bucket_key] = active_timestamps

            return fn(*args, **kwargs)

        return wrapper

    return decorator
