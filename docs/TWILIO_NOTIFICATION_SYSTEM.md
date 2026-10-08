# UPI Guardian — Twilio Notification System

## 1. Overview
The Twilio Notification System provides automated, multi-channel alerting (SMS and Voice Calls) to verified caregivers when Phase 6 Risk Fusion Engine identifies high-risk or critical activity.

---

## 2. Mandatory Safety & Privacy Principles
1. **Advisory Wording Only**:
   - The system is an early-warning risk assessment tool.
   - **Never claim**: `"Fraud confirmed"` or `"Bank account compromised"`.
   - **Always state**: `"Potential scam detected"`, `"High-risk activity detected"`, or `"Critical-risk activity detected"`.
   - Explicit disclaimer included: `"This is an automated risk alert, not a confirmed fraud determination."`
2. **Data Minimization & Masking**:
   - Phone numbers are masked (e.g. `+91 98*** **210`).
   - Payee handles are masked (e.g. `ra***r@okhdfcbank`).
   - PINs, OTPs, bank passwords, and raw SMS tokens are strictly excluded from messages.

---

## 3. Configuration & Safe Fallback
Environment variables:
```bash
TWILIO_ENABLED=false
TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_PHONE=+1XXXXXXXXXX
```
- **Safe Mock Mode**:
  - When `TWILIO_ENABLED=false` or credentials are not supplied, `MockTwilioClient` is used.
  - Generates simulated provider IDs (`SM_MOCK_<hex>`, `CA_MOCK_<hex>`).
  - No outbound HTTP requests or charges occur.
  - Pytest test suites and development environments always operate safely.

---

## 4. Message Templates

### SMS Alert Format
```
UPI Guardian Alert:
Critical-risk activity detected for Ramesh Chandra Sharma.

Risk Level: CRITICAL
Risk Score: 92/100
Transaction: ₹75,000.00
Recipient: po***e@axisbank
Reason: Suspicious communication followed by an unusual transaction pattern.

Please contact the user and verify the transaction through an official channel.

This is an automated risk alert, not a confirmed fraud determination.
```

### Voice Call Format (TwiML)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Aditi" language="en-IN">
    UPI Guardian emergency alert. A critical risk event has been detected for Ramesh Chandra Sharma.
    Please contact them immediately and verify any pending transaction through an official bank or UPI support channel.
    This is an automated risk warning and not a confirmed fraud determination.
  </Say>
  <Pause length="1"/>
  <Say voice="Polly.Aditi" language="en-IN">Thank you. Goodbye.</Say>
</Response>
```

---

## 5. Idempotency & Rate Limiting
- **Deduplication Key**: Composite of `(risk_event_id, caregiver_id, channel)`.
  - If a notification for the same tuple has already been sent or is pending, subsequent dispatches are skipped.
- **Hourly Throttle**:
  - Maximum 5 alerts per caregiver per hour by default (`max_notifications_per_hour`).
- **Caregiver Acknowledgement**:
  - Caregivers can acknowledge notifications via `POST /api/notifications/<id>/acknowledge`.
