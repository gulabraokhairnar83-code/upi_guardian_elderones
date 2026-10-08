"""UPI Guardian - Notification Enums and Data Models."""

from enum import Enum


class NotificationChannel(str, Enum):
    SMS = "SMS"
    VOICE = "VOICE"


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENDING = "SENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"


class NotificationType(str, Enum):
    RISK_ALERT = "RISK_ALERT"
    EMERGENCY_ESCALATION = "EMERGENCY_ESCALATION"


class CaregiverStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    DISABLED = "DISABLED"
