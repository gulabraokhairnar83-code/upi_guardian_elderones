# UPI Guardian - MongoDB Atlas Database Implementation

> **Document Version:** 1.0  
> **Phase:** Phase 3 MongoDB Atlas Database Implementation  
> **Date:** October 8, 2026  

---

## 1. Executive Summary

In **Phase 3**, the database layer for **UPI Guardian** was implemented to store, query, and index financial fraud detection events, synthetic transactions, elder user profiles, caregiver directories, and message analysis logs using **MongoDB Atlas**.

The database architecture features:
- **Resilient Connection Handling:** Connects to MongoDB Atlas cluster via PyMongo with automated retry and fallback to `mongomock` when running tests or offline.
- **Strict Data Contracts:** Schema models compatible with both future scikit-learn ML features and existing React 19 UI presentation contracts.
- **Repository Pattern:** Decoupled Data Access Objects (DAOs) isolating database persistence from business services and REST controllers.
- **Security:** Zero hardcoded credentials; connection strings are loaded via `MONGODB_URI` environment variable.

---

## 2. Environment Variables

Configured in `.env`:

```bash
# MongoDB Atlas Connection URI
# Example: mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
MONGODB_URI=

# Target Database Name
MONGODB_DATABASE=upi_guardian_dev

# Mock Database Override (true/false)
USE_MOCK_DB=true
```

---

## 3. Collections & Schemas

### 3.1 `users`
Stores user demographic profiles and security configurations.
- `user_id` (String, indexed)
- `name` (String)
- `age` (Integer)
- `location` (String)
- `phone` (String, indexed)
- `email` (String, unique indexed)
- `role` (String: `"elder"` | `"caregiver"`)
- `accountSafetyStatus` (String: `"Protected"` | `"At Risk"`)
- `twoFactorEnabled` (Boolean)
- `loginAlertsEnabled` (Boolean)
- `is_synthetic` (Boolean)

### 3.2 `transactions`
Contains 24+ baseline transactions and real-time payment entries with ML anomaly parameters.
- `id` (String, unique indexed: e.g. `"TXN-UG-928401"`)
- `user_id` (String, indexed)
- `amount` (Float)
- `timestamp` (ISO String / DateTime, indexed)
- `payee` (String, indexed)
- `transaction_type` (String: `"P2P"` | `"P2M"`)
- `is_new_payee` (Boolean)
- `historical_average` (Float)
- `historical_std_dev` (Float)
- `behavioral_deviation` (Float)
- `velocity` (Integer)
- `unusual_time` (Boolean)
- `anomaly_score` (Float: 0.0 - 1.0)
- `communication_risk` (Float: 0.0 - 1.0)
- `final_risk_score` (Integer: 0 - 100)
- `risk_level` (String: `"safe"` | `"review"` | `"high"` | `"critical"`, indexed)
- `explanation` (String)
- `analyzed_at` (ISO String)
- *Frontend compatibility fields:* `date`, `time`, `location`, `status`, `newPayee`, `upiId`, `device`.

### 3.3 `alerts`
Stores prioritized financial safety warnings.
- `id` (Integer, unique indexed)
- `user_id` (String, indexed)
- `transaction_id` (String)
- `level` (String: `"critical"` | `"high"` | `"review"`, indexed)
- `amount` (Float)
- `title` (String)
- `detail` (String)
- `time` (String)
- `risk` (Integer)
- `status` (String: `"pending"` | `"resolved"`, indexed)

### 3.4 `analyzed_messages`
Audit trail of scanned SMS messages and phone call transcripts.
- `message_id` (String, indexed)
- `user_id` (String, indexed)
- `text` (String)
- `type` (String: `"sms"` | `"call"`, indexed)
- `risk_score` (Integer)
- `level` (String)
- `is_suspicious` (Boolean)
- `detected_patterns` (Array of Strings)
- `explanation` (String)
- `recommendations` (Array of Strings)
- `analyzed_at` (ISO String, indexed)

### 3.5 `risk_events`
Chronological threat progression timeline (used on Explainable AI Fusion view).
- `event_id` (String)
- `user_id` (String, indexed)
- `time` (String)
- `text` (String)
- `event_type` (String: `"SMS_ALERT"`, `"CALL_ALERT"`, `"TRANSACTION_ANOMALY"`, etc.)
- `risk_score` (Integer)

### 3.6 `caregivers`
Authorized emergency contacts and family guardian roster.
- `caregiver_id` (String)
- `user_id` (String, indexed)
- `name` (String)
- `relation` (String: `"Son"`, `"Daughter"`, `"Trusted Contact"`)
- `phone` (String, indexed)
- `isTrusted` (Boolean)

### 3.7 `notification_preferences`
Personal preferences and accessibility mode settings.
- `user_id` (String, unique indexed)
- `profile` (Object: name, age, phone, email)
- `security` (Object: twoFactor, loginActivityAlerts)
- `alertPreferences` (Object: highRiskTransactions, scamCalls, scamSms, familyNotifications)
- `accessibility` (Object: seniorMode, highContrast, reducedMotion, voiceAssistance)

---

## 4. Index Optimization Strategy

Indexes ensure $O(\log N)$ lookups during real-time transaction ingestion:
```python
db.users.create_index("email", unique=True, sparse=True)
db.users.create_index("phone", sparse=True)

db.transactions.create_index("id", unique=True)
db.transactions.create_index("user_id")
db.transactions.create_index([("user_id", 1), ("timestamp", -1)])
db.transactions.create_index("status")
db.transactions.create_index("payee")

db.alerts.create_index("id", unique=True)
db.alerts.create_index("user_id")
db.alerts.create_index("level")
db.alerts.create_index("status")

db.analyzed_messages.create_index("user_id")
db.analyzed_messages.create_index("analyzed_at")
db.analyzed_messages.create_index("type")

db.risk_events.create_index("user_id")
db.risk_events.create_index("timestamp")

db.caregivers.create_index("user_id")
db.caregivers.create_index("phone")

db.notification_preferences.create_index("user_id", unique=True)
```

---

## 5. Endpoints Connected to Database

1. `GET /api/dashboard/summary` — Queries `TransactionRepository.count()` and `AlertRepository.list_alerts()`.
2. `GET /api/transactions` — Queries `TransactionRepository.list_transactions(status, query)`.
3. `GET /api/transactions/<id>` — Queries `TransactionRepository.get_by_id(id)`.
4. `GET /api/alerts` — Queries `AlertRepository.list_alerts(level)`.
5. `POST /api/alerts/<id>/resolve` — Updates alert in `AlertRepository.resolve_alert(id)`.
6. `GET /api/family/profile` — Computes active pending counts via `FamilyRepository.get_elder_profile()`.
7. `POST /api/family/alerts/resolve` — Resolves pending caregiver alerts in `FamilyRepository.resolve_family_alerts()`.
8. `GET /api/settings` — Retrieves preferences from `SettingsRepository.get_settings()`.
9. `PATCH /api/settings` — Updates settings with atomic `$set` upsert via `SettingsRepository.update_settings()`.
10. `POST /api/analyze-message` — Persists audit log of scanned communication in `MessageRepository.save_analysis()`.

---

## 6. Testing Strategy & Isolation

Database testing utilizes `mongomock`:
- Complete in-memory simulation of BSON queries, document projection, and updates.
- Zero network dependencies, eliminating test failures due to firewall, IP whitelisting, or offline environments.
- When `MONGODB_URI` points to a live MongoDB Atlas cluster, the connection is validated through the native `admin.command('ping')` probe.
