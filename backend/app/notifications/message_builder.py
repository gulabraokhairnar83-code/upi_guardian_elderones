"""UPI Guardian - Message Builder for Caregiver Alerts."""

import re


def mask_phone_number(phone: str) -> str:
    """Mask phone number preserving leading and trailing digits."""
    cleaned = re.sub(r"[^\d+]", "", phone or "")
    if len(cleaned) <= 5:
        return "****"
    return f"{cleaned[:3]}***{cleaned[-3:]}"


def mask_recipient(recipient: str) -> str:
    """Mask UPI ID or payee name (e.g. rajesh@okhdfcbank -> r***h@okhdfcbank)."""
    if not recipient:
        return "Unknown Payee"
    recipient = recipient.strip()
    if "@" in recipient:
        user_part, handle = recipient.split("@", 1)
        if len(user_part) <= 2:
            masked_user = user_part[0] + "***"
        else:
            masked_user = f"{user_part[:2]}***{user_part[-1]}"
        return f"{masked_user}@{handle}"
    if len(recipient) <= 4:
        return f"{recipient[:1]}***"
    return f"{recipient[:2]}***{recipient[-2:]}"


def build_caregiver_sms_text(
    elder_name: str,
    risk_level: str,
    risk_score: int | float,
    amount: int | float | None = None,
    recipient: str | None = None,
    reason: str | None = None,
) -> str:
    """Build compliant, safe caregiver SMS advisory notification."""
    level = (risk_level or "HIGH").upper()
    score = int(round(risk_score)) if risk_score is not None else 0
    safe_name = elder_name.strip() if elder_name else "Protected User"

    # Risk level advisory header
    if level == "CRITICAL":
        risk_headline = "Critical-risk activity detected"
    else:
        risk_headline = "High-risk activity detected"

    reason_text = reason or "Suspicious communication followed by an unusual transaction pattern."
    # Ensure reason never asserts confirmed fraud
    reason_text = reason_text.replace("fraud confirmed", "potential scam detected")
    reason_text = reason_text.replace("account compromised", "high-risk activity detected")

    lines = [
        "UPI Guardian Alert:",
        f"{risk_headline} for {safe_name}.",
        "",
        f"Risk Level: {level}",
        f"Risk Score: {score}/100",
    ]

    if amount is not None and amount > 0:
        lines.append(f"Transaction: ₹{amount:,.2f}")

    if recipient:
        lines.append(f"Recipient: {mask_recipient(recipient)}")

    lines.append(f"Reason: {reason_text}")
    lines.append("")
    lines.append("Please contact the user and verify the transaction through an official channel.")
    lines.append("")
    lines.append("This is an automated risk alert, not a confirmed fraud determination.")

    return "\n".join(lines)


def build_caregiver_voice_twiml(elder_name: str, risk_level: str) -> str:
    """Build safe voice alert TwiML string for automated call."""
    safe_name = elder_name.strip() if elder_name else "the protected user"
    level = (risk_level or "CRITICAL").upper()
    level_spoken = "critical risk" if level == "CRITICAL" else "high risk"

    speech_text = (
        f"UPI Guardian emergency alert. "
        f"A {level_spoken} event has been detected for {safe_name}. "
        f"Please contact them immediately and verify any pending transaction through an official bank or UPI support channel. "
        f"This is an automated risk warning and not a confirmed fraud determination."
    )

    twiml = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<Response>\n'
        f'  <Say voice="Polly.Aditi" language="en-IN">{speech_text}</Say>\n'
        f'  <Pause length="1"/>\n'
        f'  <Say voice="Polly.Aditi" language="en-IN">Thank you. Goodbye.</Say>\n'
        f'</Response>'
    )
    return twiml
