import math
import re
from datetime import datetime
from app.utils.errors import ValidationError


def validate_analyze_transaction(data: dict | None) -> dict:
    """Validate POST /api/analyze-transaction payload."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    payee = data.get("payee")
    if not payee or not isinstance(payee, str) or not payee.strip():
        raise ValidationError("Field 'payee' is required and must be a non-empty string.")

    amount = data.get("amount")
    if amount is None or not isinstance(amount, (int, float)):
        raise ValidationError("Field 'amount' is required and must be a positive number.")
    try:
        amount_val = float(amount)
        if amount_val <= 0 or not math.isfinite(amount_val):
            raise ValidationError("Field 'amount' must be a positive, finite number.")
        if amount_val > 10000000:
            raise ValidationError("Field 'amount' exceeds maximum permitted threshold (₹10,000,000).")
    except (ValueError, TypeError):
        raise ValidationError("Field 'amount' must be a valid numeric value.")

    upi_id = data.get("upiId") or data.get("upi_id")
    if not upi_id or not isinstance(upi_id, str) or not upi_id.strip():
        raise ValidationError("Field 'upiId' is required and must be a non-empty string.")
    if len(upi_id.strip()) > 100:
        raise ValidationError("Field 'upiId' must not exceed 100 characters.")

    if len(payee.strip()) > 200:
        raise ValidationError("Field 'payee' must not exceed 200 characters.")

    # Validate optional timestamp if provided
    timestamp = data.get("timestamp")
    if timestamp is not None:
        if not isinstance(timestamp, str) or not timestamp.strip():
            raise ValidationError("Field 'timestamp' must be a valid ISO timestamp string.")
        try:
            datetime.fromisoformat(timestamp.strip().replace("Z", "+00:00"))
        except ValueError:
            raise ValidationError(f"Invalid timestamp format '{timestamp}'. Expected ISO format.")

    user_id = str(data.get("user_id") or data.get("userId") or "usr_sunita_68").strip()
    txn_id = data.get("transaction_id") or data.get("transactionId")
    txn_id_str = str(txn_id).strip() if (txn_id and isinstance(txn_id, str) and str(txn_id).strip()) else None

    txn_type = str(data.get("transaction_type") or data.get("transactionType") or "P2P").strip().upper()
    if txn_type not in ("P2P", "P2M", "COLLECT", "QR", "AUTOPAY"):
        txn_type = "P2P"

    return {
        "transaction_id": txn_id_str,
        "payee": payee.strip(),
        "amount": amount_val,
        "upiId": str(upi_id).strip(),
        "user_id": user_id,
        "transaction_type": txn_type,
        "timestamp": timestamp.strip() if timestamp else None,
        "location": str(data.get("location", "Pune")).strip(),
        "device": str(data.get("device", "Sunita's phone")).strip(),
        "time": str(data.get("time", "")).strip(),
        "velocity": data.get("velocity"),
        "is_new_payee": data.get("is_new_payee", data.get("newPayee")),
        "unusual_time": data.get("unusual_time"),
    }


def validate_analyze_message(data: dict | None) -> dict:
    """Validate POST /api/analyze-message payload."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    text = data.get("text")
    if not text or not isinstance(text, str) or not text.strip():
        raise ValidationError("Field 'text' is required and must be a non-empty string.")
    if len(text.strip()) > 5000:
        raise ValidationError("Field 'text' exceeds maximum allowed length of 5000 characters.")

    raw_type = data.get("message_type") or data.get("type")
    if not raw_type or not isinstance(raw_type, str):
        raise ValidationError("Field 'message_type' is required and must be either 'sms' or 'call_transcript'.")

    type_clean = raw_type.strip().lower()
    if type_clean == "sms":
        std_type = "sms"
    elif type_clean in ("call", "call_transcript"):
        std_type = "call_transcript"
    else:
        raise ValidationError(
            f"Invalid message type '{raw_type}'. Allowed types: 'sms', 'call_transcript'."
        )

    user_id = str(data.get("user_id") or data.get("userId") or "usr_sunita_68").strip()

    return {
        "text": text.strip(),
        "message_type": std_type,
        "type": "call" if std_type == "call_transcript" else "sms",
        "user_id": user_id,
    }


def validate_settings_patch(data: dict | None) -> dict:
    """Validate PATCH /api/settings partial update payload."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    allowed_sections = {"profile", "security", "alertPreferences", "accessibility"}
    if not any(k in allowed_sections for k in data.keys()):
        raise ValidationError(
            f"Update payload must contain at least one valid section: {', '.join(allowed_sections)}"
        )

    return data


def validate_risk_analyze(data: dict | None) -> dict:
    """Validate POST /api/risk/analyze payload."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    user_id = str(data.get("user_id") or data.get("userId") or "usr_sunita_68").strip()
    txn_id = data.get("transaction_id") or data.get("transactionId") or data.get("id")

    # If transaction_id is provided without full transaction details
    if txn_id and ("amount" not in data or "payee" not in data):
        return {
            "transaction_id": str(txn_id).strip(),
            "user_id": user_id,
        }

    # Otherwise validate as full transaction payload
    validated_txn = validate_analyze_transaction(data)
    if txn_id:
        validated_txn["transaction_id"] = str(txn_id).strip()
    validated_txn["user_id"] = user_id
    return validated_txn


def validate_register(data: dict | None) -> dict:
    """Validate POST /api/auth/register payload."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    name = data.get("name")
    if not name or not isinstance(name, str) or len(name.strip()) < 2:
        raise ValidationError("Field 'name' is required and must be at least 2 characters.")
    if len(name.strip()) > 100:
        raise ValidationError("Field 'name' must not exceed 100 characters.")

    email = data.get("email")
    if not email or not isinstance(email, str) or not email.strip():
        raise ValidationError("Field 'email' is required.")

    clean_email = email.strip().lower()
    if len(clean_email) > 254:
        raise ValidationError("Field 'email' must not exceed 254 characters.")
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, clean_email):
        raise ValidationError("Field 'email' must be a valid email address.")

    password = data.get("password")
    if not password or not isinstance(password, str):
        raise ValidationError("Field 'password' is required.")

    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if len(password) > 128:
        raise ValidationError("Password must not exceed 128 characters.")
    if not any(c.isdigit() for c in password) or not any(c.isalpha() for c in password):
        raise ValidationError("Password must contain at least one letter and one number.")

    raw_role = data.get("role", "ELDER")
    if not isinstance(raw_role, str):
        raise ValidationError("Field 'role' must be a string.")
    role_clean = raw_role.strip().upper()
    if role_clean not in ("ELDER", "CAREGIVER"):
        raise ValidationError("Field 'role' must be either 'ELDER' or 'CAREGIVER'.")

    phone = data.get("phone", "")
    if phone and not isinstance(phone, str):
        raise ValidationError("Field 'phone' must be a string.")

    return {
        "name": name.strip(),
        "email": clean_email,
        "password": password,
        "role": role_clean,
        "phone": phone.strip() if phone else "",
    }


def validate_login(data: dict | None) -> dict:
    """Validate POST /api/auth/login payload."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    email = data.get("email")
    password = data.get("password")

    if not email or not isinstance(email, str) or not email.strip():
        raise ValidationError("Field 'email' is required.")
    if not password or not isinstance(password, str):
        raise ValidationError("Field 'password' is required.")

    return {
        "email": email.strip().lower(),
        "password": password,
    }


def validate_forgot_password(data: dict | None) -> dict:
    """Validate POST /api/auth/forgot-password payload."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    email = data.get("email")
    if not email or not isinstance(email, str) or not email.strip():
        raise ValidationError("Field 'email' is required.")

    clean_email = email.strip().lower()
    if len(clean_email) > 254:
        raise ValidationError("Field 'email' must not exceed 254 characters.")
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, clean_email):
        raise ValidationError("Field 'email' must be a valid email address.")

    return {
        "email": clean_email,
    }


def validate_caregiver_create(data: dict | None) -> dict:
    """Validate POST /api/caregivers payload."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    name = data.get("name")
    if not name or not isinstance(name, str) or len(name.strip()) < 2:
        raise ValidationError("Field 'name' is required and must be at least 2 characters.")

    phone = data.get("phone")
    email = data.get("email")

    if not (phone and isinstance(phone, str) and phone.strip()) and not (
        email and isinstance(email, str) and email.strip()
    ):
        raise ValidationError("At least one contact method ('phone' or 'email') is required.")

    raw_rel = data.get("relationship", "OTHER")
    if not isinstance(raw_rel, str):
        raise ValidationError("Field 'relationship' must be a string.")
    rel_clean = raw_rel.strip().upper()
    allowed_relations = {"SON", "DAUGHTER", "SPOUSE", "RELATIVE", "FRIEND", "OTHER"}
    if rel_clean not in allowed_relations:
        rel_clean = "OTHER"

    prefs = data.get("notification_preferences")
    if prefs is not None and not isinstance(prefs, dict):
        raise ValidationError("Field 'notification_preferences' must be an object if provided.")

    return {
        "name": name.strip(),
        "phone": str(phone).strip() if phone else "",
        "email": str(email).strip().lower() if email else "",
        "relationship": rel_clean,
        "notification_preferences": prefs or {},
    }


def validate_caregiver_patch(data: dict | None) -> dict:
    """Validate PATCH /api/caregivers/<caregiver_id> payload."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")

    updates: dict = {}
    if "name" in data:
        name = data["name"]
        if not isinstance(name, str) or len(name.strip()) < 2:
            raise ValidationError("Field 'name' must be at least 2 characters.")
        updates["name"] = name.strip()

    if "phone" in data:
        updates["phone"] = str(data["phone"]).strip()

    if "email" in data:
        updates["email"] = str(data["email"]).strip().lower()

    if "relationship" in data:
        rel = str(data["relationship"]).strip().upper()
        allowed_relations = {"SON", "DAUGHTER", "SPOUSE", "RELATIVE", "FRIEND", "OTHER"}
        updates["relationship"] = rel if rel in allowed_relations else "OTHER"

    if "is_active" in data:
        updates["is_active"] = bool(data["is_active"])

    if "notification_preferences" in data:
        if not isinstance(data["notification_preferences"], dict):
            raise ValidationError("Field 'notification_preferences' must be a JSON object.")
        updates["notification_preferences"] = data["notification_preferences"]

    if not updates:
        raise ValidationError("At least one field to update must be provided.")

    return updates


def validate_notification_acknowledge(data: dict | None) -> dict:
    """Validate POST /api/notifications/<id>/acknowledge payload."""
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.")
    return {
        "notes": str(data.get("notes", "")).strip(),
    }


def validate_twilio_webhook(data: dict | None) -> dict:
    """Validate POST /api/notifications/webhook delivery receipt payload."""
    if not isinstance(data, dict):
        raise ValidationError("Webhook payload must be a valid JSON or form dictionary.")

    sid = (
        data.get("MessageSid")
        or data.get("CallSid")
        or data.get("SmsSid")
        or data.get("provider_message_id")
        or data.get("sid")
    )
    if not sid or not isinstance(sid, str) or not sid.strip():
        raise ValidationError("Provider message/call identifier ('MessageSid' or 'CallSid') is required.")

    status = (
        data.get("MessageStatus")
        or data.get("CallStatus")
        or data.get("SmsStatus")
        or data.get("status")
    )
    if not status or not isinstance(status, str) or not status.strip():
        raise ValidationError("Delivery status ('MessageStatus' or 'CallStatus') is required.")

    error = data.get("ErrorCode") or data.get("error_message") or data.get("error")

    return {
        "provider_message_id": str(sid).strip(),
        "status": str(status).strip(),
        "error": str(error).strip() if error else None,
    }


