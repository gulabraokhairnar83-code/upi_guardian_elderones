# UPI Guardian — Risk-Triggered Escalation Policy

## 1. Trigger Hierarchy
The escalation workflow connects directly to Phase 6 Risk Fusion Engine output:

```
RiskFusionService (final_risk_score, risk_level)
                    ↓
           EscalationService
                    ↓
         Verified Caregiver Check
                    ↓
         Preferences & Quiet Hours
                    ↓
         Idempotency / Rate Limit Check
                    ↓
       Dispatch: Twilio SMS / Voice
                    ↓
      Audit Log: notifications Collection
```

---

## 2. Escalation Rules by Risk Level

| Risk Level | Score Range | Automatic Action | Channels |
| :--- | :--- | :--- | :--- |
| **LOW** | 0 – 39 | No caregiver notification | None |
| **MEDIUM** | 40 – 69 | Internal monitoring only | None |
| **HIGH** | 70 – 84 | Advisory caregiver alert | SMS (if preference enabled); Voice optional |
| **CRITICAL** | 85 – 100 | Emergency safety escalation | SMS (default active) + Automated Voice Call |

---

## 3. Quiet Hours Policy
- Configurable per caregiver (e.g., 22:00 to 07:00).
- **HIGH-risk alerts**: deferred or skipped during quiet hours.
- **CRITICAL-risk alerts**: **Bypass quiet hours** to guarantee elder financial safety during emergency events.

---

## 4. Caregiver Acknowledgement Workflow
1. Notification dispatched and logged with `is_acknowledged: false`.
2. Caregiver opens UI (`/alerts` or SMS link) and clicks **Acknowledge**.
3. API endpoint `POST /api/notifications/<id>/acknowledge` sets `is_acknowledged: true`, `acknowledged_at`, and `acknowledged_by`.
4. Dashboard and alerts center reflect updated safety state in real time.
