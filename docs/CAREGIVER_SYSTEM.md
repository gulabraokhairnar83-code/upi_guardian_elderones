# UPI Guardian — Caregiver Safety System

## 1. Overview
The Caregiver Safety System enables elderly users to link trusted contacts (such as adult children or relatives) who receive real-time advisory alerts when high-risk or critical financial events are detected.

---

## 2. Elder-to-Caregiver Relationship Model
- Every caregiver record is strictly tied to an authorized `elder_user_id`.
- **Ownership Isolation**:
  - An elder can only view, create, update, and deactivate their own caregivers.
  - Cross-tenant access is blocked with HTTP `403 Forbidden`.
- **Relationships Supported**:
  - `SON`
  - `DAUGHTER`
  - `SPOUSE`
  - `RELATIVE`
  - `FRIEND`
  - `OTHER`

---

## 3. Verification Lifecycle
To prevent accidental alerts or harassment, emergency notifications are only dispatched to **verified** caregivers.

1. **PENDING**: Caregiver is added by the elder. A secure verification token is generated with a 7-day expiration.
2. **VERIFIED**: The caregiver relationship is confirmed via verification endpoint or explicit owner confirmation (`is_verified: true`, `isTrusted: true`).
3. **DISABLED**: Caregiver relationship is deactivated (`is_active: false`).

---

## 4. Notification Preferences
Each caregiver record maintains granular notification preferences:
- `sms_enabled`: Boolean (default: `true`)
- `voice_enabled`: Boolean (default: `false`)
- `high_risk_enabled`: Boolean (default: `true`)
- `critical_risk_enabled`: Boolean (default: `true`)
- `quiet_hours_enabled`: Boolean (default: `false`)
- `quiet_hours_start`: `"22:00"`
- `quiet_hours_end`: `"07:00"`
- `max_notifications_per_hour`: Integer (default: `5`)

---

## 5. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/caregivers` | List caregivers for authenticated elder |
| `POST` | `/api/caregivers` | Register new caregiver (status: `PENDING`) |
| `GET` | `/api/caregivers/<id>` | View details of specific caregiver |
| `PATCH` | `/api/caregivers/<id>` | Update preferences or contact details |
| `DELETE` | `/api/caregivers/<id>` | Deactivate caregiver relationship |
| `POST` | `/api/caregivers/<id>/verify` | Verify caregiver relationship |
