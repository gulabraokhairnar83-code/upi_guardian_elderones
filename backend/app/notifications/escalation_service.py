"""UPI Guardian - Escalation Service.

Evaluates Risk Fusion output and orchestrates caregiver alerts.
"""

from datetime import datetime, timezone
import logging
import uuid
from app.db.repositories.caregiver_repository import CaregiverRepository
from app.db.repositories.user_repository import UserRepository
from app.notifications.models import NotificationChannel, NotificationType, NotificationStatus
from app.notifications.notification_repository import NotificationRepository
from app.notifications.sms_service import SmsService
from app.notifications.voice_service import VoiceService
from app.notifications.message_builder import build_caregiver_sms_text, build_caregiver_voice_twiml

logger = logging.getLogger("upi_guardian.notifications.escalation")

_caregiver_repo = CaregiverRepository()
_user_repo = UserRepository()
_notification_repo = NotificationRepository()


def is_in_quiet_hours(start_str: str, end_str: str, now_dt: datetime | None = None) -> bool:
    """Check if the current time falls inside quiet hours window (HH:MM)."""
    if not start_str or not end_str:
        return False
    try:
        if now_dt is None:
            now_dt = datetime.now()
        cur_min = now_dt.hour * 60 + now_dt.minute
        s_h, s_m = map(int, start_str.split(":"))
        e_h, e_m = map(int, end_str.split(":"))
        start_min = s_h * 60 + s_m
        end_min = e_h * 60 + e_m

        if start_min < end_min:
            return start_min <= cur_min <= end_min
        else:
            # Crosses midnight (e.g. 22:00 to 07:00)
            return cur_min >= start_min or cur_min <= end_min
    except Exception as exc:
        logger.warning("Error parsing quiet hours: %s", exc)
        return False


class EscalationService:
    """Orchestrates notification dispatch to verified caregivers based on risk level."""

    @staticmethod
    def escalate_risk_event(risk_analysis: dict, user_id: str | None = None) -> dict:
        """Process risk analysis result and dispatch alerts if HIGH or CRITICAL.

        Args:
            risk_analysis: Output from RiskFusionService.analyze_transaction_risk()
            user_id: ID of the protected elder user.
        """
        risk_level = (risk_analysis.get("risk_level") or "LOW").upper()
        risk_score = risk_analysis.get("final_risk_score", 0)
        risk_event_id = (
            risk_analysis.get("risk_event_id") or
            risk_analysis.get("transaction_id") or
            f"evt_{uuid.uuid4().hex[:12]}"
        )
        transaction_id = risk_analysis.get("transaction_id")

        # Step 14 Trigger Rules:
        # LOW: No caregiver notification
        # MEDIUM: No automatic emergency notification
        if risk_level not in ("HIGH", "CRITICAL"):
            return {
                "triggered": False,
                "reason": f"{risk_level}_RISK_NO_NOTIFICATION",
                "risk_level": risk_level,
                "dispatched": [],
            }

        elder_id = user_id or "usr_ramesh_001"
        elder_profile = _user_repo.get_by_id(elder_id) or {}
        elder_name = elder_profile.get("name", "Protected Family Member")

        # Retrieve verified active caregivers for this elder
        caregivers = _caregiver_repo.get_verified_caregivers_for_elder(elder_id)
        if not caregivers:
            logger.info("No verified active caregivers found for elder %s", elder_id)
            return {
                "triggered": True,
                "reason": "NO_VERIFIED_CAREGIVERS",
                "risk_level": risk_level,
                "dispatched": [],
            }

        # Extract transaction details for messaging
        features = risk_analysis.get("features_analyzed", {})
        tx_features = features.get("transaction_features", {})
        amount = tx_features.get("amount")
        recipient = tx_features.get("recipient") or tx_features.get("payee") or "Unknown Payee"
        reasons = risk_analysis.get("contributing_factors") or ["Suspicious activity detected."]
        reason_str = "; ".join(reasons[:2])

        dispatched_records = []

        for cg in caregivers:
            cg_id = cg["caregiver_id"]
            cg_phone = cg.get("phone", "")
            prefs = cg.get("notification_preferences", {})

            # Check if this risk level is enabled for caregiver
            if risk_level == "HIGH" and not prefs.get("high_risk_enabled", True):
                continue
            if risk_level == "CRITICAL" and not prefs.get("critical_risk_enabled", True):
                # Note: Default is True, critical safety takes precedence
                pass

            # Check quiet hours (CRITICAL bypasses quiet hours)
            if prefs.get("quiet_hours_enabled", False) and risk_level != "CRITICAL":
                if is_in_quiet_hours(prefs.get("quiet_hours_start", "22:00"), prefs.get("quiet_hours_end", "07:00")):
                    logger.info("Skipping notification to %s due to quiet hours.", cg_id)
                    continue

            # Check rate limit (max notifications per hour)
            hourly_limit = prefs.get("max_notifications_per_hour", 5)
            recent_count = _notification_repo.count_caregiver_notifications_in_window(cg_id, hours=1)
            if recent_count >= hourly_limit:
                logger.warning("Rate limit exceeded for caregiver %s (%d sent in 1h)", cg_id, recent_count)
                continue

            # --- SMS DISPATCH ---
            # Default for HIGH & CRITICAL is SMS enabled
            sms_enabled = prefs.get("sms_enabled", True)
            if sms_enabled and cg_phone:
                # Deduplication check
                existing_sms = _notification_repo.find_duplicate(
                    risk_event_id=risk_event_id,
                    caregiver_id=cg_id,
                    channel=NotificationChannel.SMS.value,
                )
                if not existing_sms:
                    sms_text = build_caregiver_sms_text(
                        elder_name=elder_name,
                        risk_level=risk_level,
                        risk_score=risk_score,
                        amount=amount,
                        recipient=recipient,
                        reason=reason_str,
                    )
                    sms_result = SmsService.send(to_phone=cg_phone, body=sms_text)
                    notif_record = {
                        "notification_id": f"notif_sms_{uuid.uuid4().hex[:10]}",
                        "user_id": elder_id,
                        "caregiver_id": cg_id,
                        "caregiver_user_id": cg.get("caregiver_user_id"),
                        "transaction_id": transaction_id,
                        "risk_event_id": risk_event_id,
                        "channel": NotificationChannel.SMS.value,
                        "notification_type": (
                            NotificationType.EMERGENCY_ESCALATION.value
                            if risk_level == "CRITICAL"
                            else NotificationType.RISK_ALERT.value
                        ),
                        "risk_level": risk_level,
                        "status": sms_result.get("status", NotificationStatus.SENT.value),
                        "provider_message_id": sms_result.get("sid"),
                        "message_preview": sms_text[:160],
                        "error_code": sms_result.get("error"),
                    }
                    saved = _notification_repo.create_notification(notif_record)
                    dispatched_records.append(saved)
                else:
                    logger.info("Deduplication: Skipped duplicate SMS for event %s to cg %s", risk_event_id, cg_id)

            # --- VOICE DISPATCH ---
            # Voice initiated if CRITICAL or voice_enabled explicitly in prefs
            voice_enabled = prefs.get("voice_enabled", False)
            if voice_enabled and cg_phone:
                existing_voice = _notification_repo.find_duplicate(
                    risk_event_id=risk_event_id,
                    caregiver_id=cg_id,
                    channel=NotificationChannel.VOICE.value,
                )
                if not existing_voice:
                    twiml = build_caregiver_voice_twiml(elder_name=elder_name, risk_level=risk_level)
                    voice_result = VoiceService.make_call(to_phone=cg_phone, twiml=twiml)
                    voice_record = {
                        "notification_id": f"notif_voice_{uuid.uuid4().hex[:10]}",
                        "user_id": elder_id,
                        "caregiver_id": cg_id,
                        "caregiver_user_id": cg.get("caregiver_user_id"),
                        "transaction_id": transaction_id,
                        "risk_event_id": risk_event_id,
                        "channel": NotificationChannel.VOICE.value,
                        "notification_type": NotificationType.EMERGENCY_ESCALATION.value,
                        "risk_level": risk_level,
                        "status": voice_result.get("status", NotificationStatus.SENT.value),
                        "provider_message_id": voice_result.get("sid"),
                        "message_preview": f"Automated voice alert dispatched to {cg_phone[:6]}****",
                        "error_code": voice_result.get("error"),
                    }
                    saved = _notification_repo.create_notification(voice_record)
                    dispatched_records.append(saved)
                else:
                    logger.info("Deduplication: Skipped duplicate Voice call for event %s to cg %s", risk_event_id, cg_id)

        return {
            "triggered": True,
            "risk_level": risk_level,
            "risk_event_id": risk_event_id,
            "caregivers_notified_count": len(dispatched_records),
            "dispatched": dispatched_records,
        }
