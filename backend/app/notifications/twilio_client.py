"""UPI Guardian - Twilio Client with Mock Provider."""

import logging
import uuid
from typing import Optional
from app.notifications.config import get_twilio_config
from app.notifications.models import NotificationStatus

logger = logging.getLogger("upi_guardian.notifications")


class MockTwilioClient:
    """Mock Twilio client for safe automated tests and offline development."""

    def __init__(self):
        self.sent_messages: list[dict] = []
        self.made_calls: list[dict] = []

    def send_sms(self, to_phone: str, body: str) -> dict:
        """Simulate sending an SMS message."""
        sid = f"SM_MOCK_{uuid.uuid4().hex[:16]}"
        record = {
            "sid": sid,
            "to": to_phone,
            "body": body,
            "status": NotificationStatus.SENT.value,
            "error": None,
        }
        self.sent_messages.append(record)
        logger.info("Mock Twilio SMS dispatched to %s (SID: %s)", to_phone[:6] + "****", sid)
        return record

    def make_call(self, to_phone: str, twiml: str) -> dict:
        """Simulate initiating a voice call."""
        sid = f"CA_MOCK_{uuid.uuid4().hex[:16]}"
        record = {
            "sid": sid,
            "to": to_phone,
            "twiml": twiml,
            "status": NotificationStatus.SENT.value,
            "error": None,
        }
        self.made_calls.append(record)
        logger.info("Mock Twilio Voice Call initiated to %s (SID: %s)", to_phone[:6] + "****", sid)
        return record


class RealTwilioClient:
    """Real Twilio REST client wrapper."""

    def __init__(self, account_sid: str, auth_token: str, from_phone: str):
        self.account_sid = account_sid
        self.from_phone = from_phone
        try:
            from twilio.rest import Client
            self.client = Client(account_sid, auth_token)
        except Exception as exc:
            logger.error("Failed to initialize Twilio REST Client: %s", exc)
            self.client = None

    def send_sms(self, to_phone: str, body: str) -> dict:
        """Send live SMS message via Twilio."""
        if not self.client:
            return {
                "sid": None,
                "status": NotificationStatus.FAILED.value,
                "error": "Twilio client not initialized.",
            }
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.from_phone,
                to=to_phone,
            )
            return {
                "sid": message.sid,
                "status": NotificationStatus.SENT.value,
                "error": None,
            }
        except Exception as exc:
            logger.error("Twilio SMS send error: %s", exc)
            return {
                "sid": None,
                "status": NotificationStatus.FAILED.value,
                "error": str(exc),
            }

    def make_call(self, to_phone: str, twiml: str) -> dict:
        """Initiate live Voice Call via Twilio."""
        if not self.client:
            return {
                "sid": None,
                "status": NotificationStatus.FAILED.value,
                "error": "Twilio client not initialized.",
            }
        try:
            call = self.client.calls.create(
                twiml=twiml,
                from_=self.from_phone,
                to=to_phone,
            )
            return {
                "sid": call.sid,
                "status": NotificationStatus.SENT.value,
                "error": None,
            }
        except Exception as exc:
            logger.error("Twilio Voice Call error: %s", exc)
            return {
                "sid": None,
                "status": NotificationStatus.FAILED.value,
                "error": str(exc),
            }


_mock_instance = MockTwilioClient()


def get_twilio_client():
    """Factory retrieving appropriate Twilio client instance."""
    cfg = get_twilio_config()
    if cfg["enabled"]:
        return RealTwilioClient(cfg["account_sid"], cfg["auth_token"], cfg["from_phone"])
    return _mock_instance


def get_mock_twilio_client() -> MockTwilioClient:
    """Retrieve shared mock instance for unit tests inspection."""
    return _mock_instance
