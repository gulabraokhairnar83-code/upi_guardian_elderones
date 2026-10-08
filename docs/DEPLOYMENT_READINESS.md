# UPI Guardian — Deployment Readiness & Production Operations Guide

**Phase**: Phase 9  
**Status**: Ready for Cloud Provisioning (Phase 10)  
**Security Baseline**: Audited, Hardened, 160/160 Tests Passing  

---

## 1. Overview & Scope

This document provides a comprehensive operational readiness assessment for the deployment of **UPI Guardian**. It details the architectural prerequisites, environment tiers, security checklists, and configuration requirements necessary to transition the platform into production cloud infrastructure (such as Render, Vercel, or AWS).

> [!IMPORTANT]  
> In accordance with Phase 9 execution rules, **live cloud deployment has NOT been executed**. Live accounts, credit cards, real Twilio charges, and production database clusters remain intentionally uncommitted until Phase 10.

---

## 2. Environment Tiers

The application defines three strictly isolated operating environments:

```
+-----------------------------------------------------------------------------------+
|                                 ENVIRONMENT TIERS                                 |
+----------------------+----------------------------+-------------------------------+
| Tier                 | Database                   | External Services             |
+----------------------+----------------------------+-------------------------------+
| DEVELOPMENT          | MongoDB Atlas Dev or       | Mock Twilio Client            |
|                      | mongomock in-memory        | Mock API Toggle Supported     |
+----------------------+----------------------------+-------------------------------+
| TESTING (CI/CD)      | Isolated mongomock         | Mock Twilio Client            |
|                      | Rate limiting relaxed      | In-memory state reset         |
+----------------------+----------------------------+-------------------------------+
| PRODUCTION           | MongoDB Atlas Dedicated    | Real Twilio REST API          |
|                      | IP Whitelisted Cluster     | Strict CORS, HSTS, Rate Limit |
+----------------------+----------------------------+-------------------------------+
```

---

## 3. Production Configuration Checklist

Before promoting UPI Guardian to production, ensure every parameter in `backend/.env.production.example` and `frontend-magic-wand-07-main/.env.production.example` is populated:

### Backend Parameters
- `FLASK_ENV=production`: Disables Flask development features, enables production security guards.
- `SECRET_KEY`: High-entropy 64-character random string (e.g. generated via `secrets.token_hex(32)`).
- `JWT_SECRET_KEY`: Distinct, cryptographically strong secret used exclusively for signing HS256 tokens.
- `JWT_ACCESS_TOKEN_EXPIRES=900`: 15-minute short token lifetime.
- `JWT_REFRESH_TOKEN_EXPIRES=604800`: 7-day token refresh window.
- `CORS_ORIGINS`: Comma-separated list of approved frontend domain names (e.g. `https://guardian.yourdomain.com`).
- `ENABLE_HSTS=true`: Enforces Strict-Transport-Security over HTTPS.
- `RATE_LIMIT_ENABLED=true`: Enforces sliding-window rate limiting on auth and escalation endpoints.
- `MONGODB_URI`: Production MongoDB Atlas connection string with replica set and SSL enabled.
- `MONGODB_DATABASE=upi_guardian_prod`: Production database namespace.
- `USE_MOCK_DB=false`: Forces reliance on real Atlas cluster; prevents silent in-memory fallback.
- `TWILIO_ENABLED=true`: Enables live telecom dispatch (set only after testing approved sender IDs).
- `TWILIO_ACCOUNT_SID`: Verified Twilio Account SID.
- `TWILIO_AUTH_TOKEN`: Verified Twilio Auth Token.
- `TWILIO_FROM_PHONE`: Approved 10DLC or Toll-Free number registered for SMS/Voice.

### Frontend Parameters
- `VITE_API_BASE_URL`: Full HTTPS URL to the deployed backend service (e.g. `https://api.yourdomain.com/api`).
- `VITE_USE_MOCK_API=false`: Enforces live API communication.

---

## 4. Database Readiness (MongoDB Atlas)

1. **Network Access**:
   - Do **NOT** use `0.0.0.0/0` (universal access).
   - Add only the static outbound IP addresses of the backend application hosts (e.g., Render outbound IPs, AWS Elastic IPs, or VPC peering).
2. **Database User**:
   - Create a dedicated database user with `readWrite` permissions scoped strictly to the `upi_guardian_prod` database.
3. **Index Pre-Validation**:
   - The application automatically ensures the 9 required indexes on boot, including unique constraints on users, transactions, and the TTL index on `revoked_tokens`.
4. **Automated Backups**:
   - Enable Continuous Cloud Backup in MongoDB Atlas with a 7-day minimum retention window.

---

## 5. Machine Learning Runtime Verification

The machine learning models are pre-packaged and verified:
- **Transaction Anomaly Detector**: `backend/app/ml/models/artifacts/transaction_anomaly_detector.joblib`
  - Pre-trained Isolation Forest model.
  - Sits in read-only runtime directory.
  - Fast inference ($< 5\text{ms}$).
- **Scam Communication Classifier**: `backend/app/nlp/models/artifacts/scam_classifier.joblib`
  - Pre-trained TF-IDF Vectorizer + Logistic Regression model.
  - Sits in read-only runtime directory.
  - Fast inference ($< 8\text{ms}$).
- **No Online Retraining**:
  - Models run strictly in inference mode. No background GPU training or model retraining occurs during live transactions.

---

## 6. Telecom & Twilio Setup (Phase 10 Transition)

When activating live Twilio in Phase 10:
1. Complete A2P 10DLC (Application-to-Person) registration if dispatching SMS to Indian or US telecom numbers to prevent carrier filtering.
2. Verify verified sender numbers and voice caller IDs in the Twilio Console.
3. Register the Webhook URL `https://api.yourdomain.com/api/notifications/webhook` in the Twilio Phone Number configuration to receive real-time delivery receipts.

---

## 7. Containerized Runtime Architecture

- **Backend**:
  - Image: `python:3.11-slim`
  - Web Server: `gunicorn` with 2 workers and 4 threads per worker.
  - User: Non-root `appuser`.
  - Memory Requirement: Minimum 512MB RAM.
- **Frontend**:
  - Built with Node 20 / Vite into production static assets.
  - Served via minimal static runner or edge CDN (e.g., Cloudflare Pages, Vercel, or Nginx).

---

## 8. Health Monitoring & Probes

- **Liveness & Readiness**:
  - Endpoint: `GET /api/health`
  - Expected Response:
    ```json
    {
      "status": "healthy",
      "service": "upi-guardian-backend",
      "version": "1.0.0",
      "database": {
        "connected": true,
        "engine": "MongoDB Atlas",
        "status": "healthy"
      }
    }
    ```
  - Probe Frequency: Recommended every 30 seconds with 5-second timeout.
