# UPI Guardian - REST API Specification

> **Document Version:** 1.0  
> **Base URL:** `http://localhost:5000/api`  
> **Content-Type:** `application/json`  

---

## 1. System Endpoints

### 1.1 Health Check
- **Route:** `GET /api/health`
- **Description:** Verifies service uptime, status, and semantic version.
- **Response `200 OK`:**
```json
{
  "service": "upi-guardian-backend",
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 2. Dashboard Endpoints

### 2.1 Dashboard Summary
- **Route:** `GET /api/dashboard/summary`
- **Description:** Returns high-level fraud monitoring status, KPI metrics, 24-hour activity distribution, and 3 most recent alerts.
- **Response `200 OK`:**
```json
{
  "systemStatus": "OPERATIONAL",
  "accountStatus": "Protected",
  "currentRiskScore": 27,
  "riskLevel": "safe",
  "riskSummary": "Low risk. No immediate action needed.",
  "kpis": [
    {"label": "Total Transactions", "value": "248", "trend": "+12%", "tone": "info"},
    {"label": "Safe Transactions", "value": "221", "trend": "+8%", "tone": "safe"},
    {"label": "Suspicious", "value": "18", "trend": "-3%", "tone": "warning"},
    {"label": "High Risk Alerts", "value": "9", "trend": "+2", "tone": "danger"},
    {"label": "Current Risk Score", "value": "27/100", "trend": "Normal", "tone": "safe"},
    {"label": "Scams Detected", "value": "7", "trend": "+100%", "tone": "ai"}
  ],
  "activity": [
    {"time": "8 AM", "normal": 1200, "suspicious": 0, "high": 0},
    {"time": "11 PM", "normal": 900, "suspicious": 3500, "high": 48000}
  ],
  "recentAlerts": [
    {
      "id": 1,
      "level": "critical",
      "amount": 48000,
      "title": "Large payment to a new payee",
      "detail": "Made at 11:47 PM shortly after a suspicious call.",
      "time": "12 minutes ago",
      "risk": 92,
      "status": "pending"
    }
  ]
}
```

---

## 3. Transactions Endpoints

### 3.1 List Transactions
- **Route:** `GET /api/transactions`
- **Query Parameters:**
  - `status` *(optional)*: Filter by risk level (`safe`, `review`, `high`, `critical`, or `all`).
  - `q` *(optional)*: Search query matching payee name or transaction ID.
- **Response `200 OK`:** Array of transaction objects.
```json
[
  {
    "id": "TXN-UG-928401",
    "date": "29 Sep 2026",
    "time": "11:42 PM",
    "payee": "Rahul Sharma",
    "amount": 35000,
    "location": "Pune",
    "risk": 89,
    "status": "critical",
    "newPayee": true,
    "upiId": "demo.payee1@upi",
    "device": "New Android device"
  }
]
```

### 3.2 Get Transaction Details
- **Route:** `GET /api/transactions/<transaction_id>`
- **Response `200 OK`:** Single transaction object.
- **Response `404 Not Found`:**
```json
{
  "error": "Transaction with ID '...' was not found.",
  "status": 404
}
```

### 3.3 Analyze Transaction (ML Isolation Forest Inference)
- **Route:** `POST /api/analyze-transaction`
- **Request Body:**
```json
{
  "transaction_id": "TXN-UG-928499",
  "payee": "Shadow Loan Agent",
  "amount": 75000,
  "upiId": "agent@shadowloan",
  "user_id": "usr_sunita_68",
  "transaction_type": "P2P",
  "time": "11:45 PM",
  "location": "Pune",
  "device": "New Android device"
}
```
- **Validation Rules:**
  - `payee`: Required non-empty string.
  - `amount`: Required positive finite number.
  - `upiId`: Required non-empty string.
  - `timestamp`: Optional ISO timestamp string (validated format if present).
- **Response `200 OK` (Phase 4 Real ML Response):**
```json
{
  "success": true,
  "transaction_id": "TXN-UG-928499",
  "transactionId": "TXN-UG-928499",
  "payee": "Shadow Loan Agent",
  "amount": 75000.0,
  "riskScore": 89,
  "riskLevel": "critical",
  "recommendedAction": "block",
  "contributingFactors": [
    { "name": "amount_deviation", "score": 75000.0 },
    { "name": "new_payee", "score": 1 },
    { "name": "unusual_time", "score": 1 },
    { "name": "behavioral_deviation", "score": 89.4 }
  ],
  "explanation": "Critical anomaly detected (score 89.4/100). Immediate safety review warranted due to suspicious amount deviation, new payee, unusual time.",
  "analysis": {
    "anomaly_score": 89.4,
    "anomaly": true,
    "risk_level": "CRITICAL",
    "model_version": "1.0.0",
    "features": {
      "amount": 75000.0,
      "z_score_deviation": 64.42,
      "velocity": 1.0,
      "is_new_payee": 1.0,
      "unusual_time": 1.0
    },
    "contributing_factors": [
      {
        "factor": "amount_deviation",
        "value": 75000.0,
        "severity": "CRITICAL",
        "message": "Transaction amount of ₹75,000.00 is exceptionally higher than the user's historical average of ₹2,850.00 (z-score: 64.42)."
      },
      {
        "factor": "new_payee",
        "value": 1,
        "severity": "HIGH",
        "message": "Payment recipient has never been transacted with previously by this account."
      },
      {
        "factor": "unusual_time",
        "value": 1,
        "severity": "HIGH",
        "message": "Transaction initiated during late night / early morning hours (11:00 PM – 5:00 AM)."
      },
      {
        "factor": "behavioral_deviation",
        "value": 89.4,
        "severity": "CRITICAL",
        "message": "Multiple compounding risk signals diverge sharply from the elder user's baseline behavior."
      }
    ],
    "explanation": "Critical anomaly detected (score 89.4/100). Immediate safety review warranted due to suspicious amount deviation, new payee, unusual time.",
    "recommended_action": "block"
  },
  "alert": {
    "id": 4,
    "user_id": "usr_sunita_68",
    "transaction_id": "TXN-UG-928499",
    "alert_type": "TRANSACTION_ANOMALY",
    "level": "critical",
    "amount": 75000.0,
    "title": "Critical transaction anomaly detected",
    "detail": "Critical anomaly detected (score 89.4/100). Immediate safety review warranted due to suspicious amount deviation, new payee, unusual time.",
    "time": "Just now",
    "risk": 89,
    "status": "pending",
    "created_at": "2026-10-08T12:00:00Z"
  }
}
```
- **Response `400 Bad Request`:**
```json
{
  "error": "Field 'amount' is required and must be a positive number.",
  "status": 400
}
```

---

## 4. Alerts Endpoints

### 4.1 List Alerts
- **Route:** `GET /api/alerts`
- **Query Parameters:**
  - `level` *(optional)*: Filter by severity (`critical`, `high`, `review`, or `all`).
- **Response `200 OK`:** Array of alert objects.

### 4.2 Resolve Alert
- **Route:** `POST /api/alerts/<alert_id>/resolve`
- **Response `200 OK`:**
```json
{
  "success": true,
  "id": 1,
  "message": "Alert 1 marked as resolved."
}
```
- **Response `404 Not Found`:** If alert ID is not found.
- **Response `400 Bad Request`:** If alert ID is not an integer.

---

## 5. Family & Caregiver Endpoints

### 5.1 Get Family Profile
- **Route:** `GET /api/family/profile`
- **Response `200 OK`:**
```json
{
  "id": "elder-sunita-01",
  "name": "Sunita Devi",
  "age": 68,
  "location": "Pune",
  "accountSafetyStatus": "Protected",
  "phone": "+91 ••••• ••410",
  "email": "sunita.demo@example.com",
  "twoFactorEnabled": true,
  "loginAlertsEnabled": true,
  "metrics": {
    "currentRiskScore": 27,
    "todayTransactionsCount": 8,
    "activeAlertsCount": 2,
    "scamCommunicationsCount": 3
  }
}
```

### 5.2 Resolve Family Alerts
- **Route:** `POST /api/family/alerts/resolve`
- **Response `200 OK`:**
```json
{
  "success": true,
  "message": "All urgent family alerts have been marked as resolved.",
  "profile": { ... }
}
```

---

## 6. Message Scam Analysis Endpoints

### 6.1 Analyze Message (NLP Scam Detection Inference)
- **Route:** `POST /api/analyze-message`
- **Request Body:**
```json
{
  "user_id": "usr_sunita_68",
  "message_type": "sms",
  "text": "URGENT: Your SBI account has been compromised. Send OTP immediately to verify reversal."
}
```
*Note: Also accepts legacy format `{"text": "...", "type": "sms" | "call"}`.*
- **Validation Rules:**
  - `text`: Required non-empty string.
  - `message_type` or `type`: Required string (`"sms"` or `"call_transcript"` / `"call"`).
- **Response `200 OK` (Phase 5 Real NLP Response):**
```json
{
  "success": true,
  "isSuspicious": true,
  "riskScore": 92,
  "level": "critical",
  "title": "POTENTIAL SCAM DETECTED",
  "detectedPatterns": [
    "OTP_REQUEST",
    "ACCOUNT_BLOCK_THREAT"
  ],
  "explanation": "Potential scam detected (model confidence: 92.4%). The communication exhibits high-risk coercive indicators including otp request, account block threat.",
  "recommendations": [
    "Do NOT share your OTP, UPI PIN, or passwords with anyone. Legitimate bank officials never ask for secret PINs over calls or SMS."
  ],
  "analysis": {
    "classification": "SCAM",
    "scam_probability": 92.4,
    "risk_level": "CRITICAL",
    "message_type": "sms",
    "categories": [
      "OTP_REQUEST",
      "ACCOUNT_BLOCK_THREAT"
    ],
    "suspicious_phrases": [
      "send OTP immediately",
      "account has been compromised"
    ],
    "explanation": "Potential scam detected (model confidence: 92.4%). The communication exhibits high-risk coercive indicators including otp request, account block threat.",
    "recommended_action": "Do NOT share your OTP, UPI PIN, or passwords with anyone. Legitimate bank officials never ask for secret PINs over calls or SMS."
  },
  "alert": {
    "id": 5,
    "user_id": "usr_sunita_68",
    "alert_type": "SCAM_COMMUNICATION",
    "level": "critical",
    "title": "Suspicious communication detected",
    "detail": "Potential scam detected (model confidence: 92.4%)...",
    "time": "Just now",
    "risk": 92,
    "status": "pending"
  },
  "isDevelopmentStub": false
}
```
- **Response `400 Bad Request`:**
```json
{
  "error": "Field 'text' is required and must be a non-empty string.",
  "status": 400
}
```

---

## 7. Settings Endpoints

### 7.1 Get Settings
- **Route:** `GET /api/settings`
- **Response `200 OK`:** User preferences, security settings, and accessibility options.

### 7.2 Update Settings
- **Route:** `PATCH /api/settings`
- **Request Body:** Partial settings payload (e.g., `{"accessibility": {"seniorMode": true}}`).
- **Response `200 OK`:** Full updated settings object.

---

## 8. Multi-Signal Risk Fusion Endpoints

### 8.1 Analyze Transaction Risk (Fusion Engine)
- **Route:** `POST /api/risk/analyze`
- **Description:** Combines Isolation Forest transaction anomaly risk (Phase 4), NLP communication scam risk (Phase 5), behavioral deviation, payee novelty, velocity, and 120-minute temporal correlation into an explainable composite risk score.
- **Request Body (Option A - By Transaction ID):**
```json
{
  "user_id": "usr_sunita_68",
  "transaction_id": "TXN-UG-928401"
}
```
- **Request Body (Option B - Inline Transaction Details):**
```json
{
  "user_id": "usr_sunita_68",
  "amount": 48000.0,
  "payee": "Electricity Collection Officer",
  "upiId": "elec.officer@okaxis",
  "is_new_payee": true,
  "velocity": 3,
  "timestamp": "2026-10-08T20:00:00Z"
}
```
- **Response `200 OK`:**
```json
{
  "success": true,
  "analysis": {
    "transaction_id": "TXN-UG-928401",
    "user_id": "usr_sunita_68",
    "transaction_anomaly_score": 89.4,
    "communication_risk_score": 96.2,
    "behavioral_deviation_score": 82.0,
    "new_payee_score": 100.0,
    "velocity_score": 70.0,
    "temporal_correlation_score": 95.0,
    "correlation_boost": 10.0,
    "final_risk_score": 97.0,
    "risk_level": "CRITICAL",
    "top_contributing_factors": [
      "Transaction occurred shortly after suspicious communication",
      "Suspicious communication detected",
      "Unusual transaction amount",
      "New or unfamiliar payee",
      "Unusual payment frequency"
    ],
    "explanation": "High-risk activity detected because an unusual transaction occurred shortly after a suspicious communication. The transaction involves significant deviations from your normal pattern.",
    "recommended_action": "Do not proceed. Contact a trusted caregiver or official bank/UPI support using a verified contact method.",
    "communication_id": "msg_scam_01",
    "alert_created": true
  }
}
```
- **Response `400 Bad Request`:**
```json
{
  "error": "Field 'amount' must be a positive, finite number.",
  "status": 400
}
```
- **Response `404 Not Found`:**
```json
{
  "error": "Transaction with ID 'TXN_DOES_NOT_EXIST' was not found in the database.",
  "status": 404
}
```

### 8.2 List Recent Risk Events
- **Route:** `GET /api/risk/events?user_id=usr_sunita_68&limit=20`
- **Description:** Retrieves historical audit log of multi-signal fused risk assessments.
- **Response `200 OK`:**
```json
{
  "success": true,
  "events": [
    {
      "id": "re_87f9c2d1",
      "event_id": "re_87f9c2d1",
      "user_id": "usr_sunita_68",
      "transaction_id": "TXN-UG-928401",
      "final_risk_score": 97.0,
      "risk_level": "CRITICAL",
      "created_at": "2026-10-08T20:00:00Z"
    }
  ],
  "count": 1
}
```

---

## 9. Authentication Endpoints (Phase 8)

### 9.1 User Registration
- **Route:** `POST /api/auth/register`
- **Payload:** `{"name": "...", "email": "...", "password": "...", "phone": "...", "role": "ELDER"|"CAREGIVER"}`
- **Response `201 Created`:** Returns `user`, `access_token`, and `refresh_token`.

### 9.2 User Login
- **Route:** `POST /api/auth/login`
- **Payload:** `{"email": "...", "password": "..."}`
- **Response `200 OK`:** Returns `user`, `access_token`, and `refresh_token`.

### 9.3 Token Refresh
- **Route:** `POST /api/auth/refresh`
- **Payload:** `{"refresh_token": "..."}`
- **Response `200 OK`:** Returns new `access_token`.

### 9.4 Token Revocation / Logout
- **Route:** `POST /api/auth/logout`
- **Header:** `Authorization: Bearer <token>`
- **Response `200 OK`:** Blacklists current token on server.

### 9.5 Current Profile
- **Route:** `GET /api/auth/me`
- **Header:** `Authorization: Bearer <token>`
- **Response `200 OK`:** Returns authenticated user profile.

---

## 10. Caregiver Endpoints (Phase 8)

### 10.1 List Caregivers
- **Route:** `GET /api/caregivers`
- **Header:** `Authorization: Bearer <token>`
- **Response `200 OK`:** Returns list of active caregivers for current elder user.

### 10.2 Create Caregiver
- **Route:** `POST /api/caregivers`
- **Header:** `Authorization: Bearer <token>`
- **Payload:** `{"name": "...", "phone": "...", "email": "...", "relationship": "SON"|"DAUGHTER"|"SPOUSE"|..., "notification_preferences": {...}}`
- **Response `201 Created`:** Caregiver record with `status: "PENDING"`.

### 10.3 Get Caregiver
- **Route:** `GET /api/caregivers/<caregiver_id>`
- **Header:** `Authorization: Bearer <token>`

### 10.4 Update Caregiver
- **Route:** `PATCH /api/caregivers/<caregiver_id>`
- **Header:** `Authorization: Bearer <token>`
- **Payload:** Partial fields or updated `notification_preferences`.

### 10.5 Delete / Deactivate Caregiver
- **Route:** `DELETE /api/caregivers/<caregiver_id>`
- **Header:** `Authorization: Bearer <token>`

### 10.6 Verify Caregiver
- **Route:** `POST /api/caregivers/<caregiver_id>/verify`
- **Header:** `Authorization: Bearer <token>`
- **Payload:** `{"token": "..."}` (optional for account owner)

---

## 11. Notification & Telemetry Endpoints (Phase 8)

### 11.1 List Notification History
- **Route:** `GET /api/notifications?limit=50`
- **Header:** `Authorization: Bearer <token>`
- **Response `200 OK`:** List of automated SMS and voice dispatches.

### 11.2 Acknowledge Notification
- **Route:** `POST /api/notifications/<notification_id>/acknowledge`
- **Header:** `Authorization: Bearer <token>`
- **Response `200 OK`:** Updated record with `is_acknowledged: true`, `acknowledged_at`, `acknowledged_by`.

### 11.3 Trigger Escalation
- **Route:** `POST /api/notifications/escalate`
- **Header:** `Authorization: Bearer <token>`
- **Payload:** Risk analysis event dictionary.
- **Rate Limit:** 20 requests / minute / user.

### 11.4 Provider Delivery Receipt Webhook (Phase 9)
- **Route:** `POST /api/notifications/webhook`
- **Authentication:** Provider signature validation / Callback payload inspection.
- **Description:** Receives delivery status callbacks from Twilio or SMS gateways (`delivered`, `undelivered`, `failed`, `sent`). Updates internal dispatch records safely.
- **Payload:**
```json
{
  "MessageSid": "SM_MOCK_262e8cfa67a14d0e",
  "MessageStatus": "delivered",
  "ErrorCode": null
}
```
- **Response `200 OK`:**
```json
{
  "success": true,
  "message": "Webhook processed safely.",
  "provider_message_id": "SM_MOCK_262e8cfa67a14d0e",
  "status": "delivered",
  "updated": true
}
```

---

## 12. Security Architecture & HTTP Headers (Phase 9)

All API responses automatically attach standard OWASP / WCAG security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Content-Security-Policy: default-src 'self'; frame-ancestors 'none';`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (when `ENABLE_HSTS=true` or in production over HTTPS)

### In-Memory Sliding Window Rate Limiting
- `POST /api/auth/register`: 10 requests / min / IP
- `POST /api/auth/login`: 15 requests / min / IP
- `POST /api/auth/refresh`: 30 requests / min / IP
- `POST /api/notifications/escalate`: 20 requests / min / user
- **Rate Limit Exceeded:** Returns HTTP `429 Too Many Requests` with a `Retry-After` header.



