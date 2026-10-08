"""UPI Guardian - SMS Notification Service."""

import logging
from app.notifications.twilio_client import get_twilio_client

logger = logging.getLogger("upi_guardian.notifications.sms")


class SmsService:
    """Service for dispatching SMS notifications to caregivers."""

    @staticmethod
    def send(to_phone: str, body: str) -> dict:
        """Send SMS alert to designated phone number.

        Returns dict containing provider status and sid.
        """
        if not to_phone:
            logger.warning("SMS dispatch attempted with empty phone number.")
            return {"sid": None, "status": "FAILED", "error": "Recipient phone is missing."}

        client = get_twilio_client()
        return client.send_sms(to_phone=to_phone, body=body)
