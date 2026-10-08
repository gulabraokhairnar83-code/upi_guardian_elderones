"""UPI Guardian - Voice Notification Service."""

import logging
from app.notifications.twilio_client import get_twilio_client

logger = logging.getLogger("upi_guardian.notifications.voice")


class VoiceService:
    """Service for initiating automated voice calls to caregivers."""

    @staticmethod
    def make_call(to_phone: str, twiml: str) -> dict:
        """Initiate voice call with TwiML instructions.

        Returns dict containing provider status and sid.
        """
        if not to_phone:
            logger.warning("Voice call attempted with empty phone number.")
            return {"sid": None, "status": "FAILED", "error": "Recipient phone is missing."}

        client = get_twilio_client()
        return client.make_call(to_phone=to_phone, twiml=twiml)
