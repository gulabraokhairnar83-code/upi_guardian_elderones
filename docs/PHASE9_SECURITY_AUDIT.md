# UPI Guardian — Phase 9 Security Audit & Vulnerability Assessment

**Audit Date**: October 9, 2026  
**Project Phase**: Phase 9 (Production Hardening, Security Audit, Accessibility & Deployment Readiness)  
**Baseline Test Status**: 160/160 automated tests passing (100% pass rate)  
**Status**: COMPLETED & VERIFIED  

---

## Executive Summary

As part of Phase 9, a full-scope security and architectural audit of the UPI Guardian ecosystem was conducted across the backend Flask service, React/TanStack frontend, database integration, ML/NLP runtime models, notification infrastructure, containerization, and configuration layers.

A repository-wide automated secret scan detected **0 leaked credentials, keys, or connection strings**. All sensitive credentials are decoupled into environment variables. Rate limiting, HTTP security headers, generic authentication error messaging, input validation boundary enforcement, and token revocation TTL have been hardened and verified by automated regression tests.

---

## 1. Current Architecture

UPI Guardian operates as a distributed defense platform designed to protect senior citizens from financial fraud and social engineering scams across UPI transactions:

- **Frontend Client**: React 19 SPA running on TanStack Router / TanStack Start with Vite. Features high-contrast themes, Senior Mode (larger tap targets, scaled typography, high-visibility alerts), and unified offline-mock / live-API capabilities.
- **Backend API**: Flask 3.0 REST application organized using Blueprints (`/api/auth`, `/api/caregivers`, `/api/notifications`, `/api/risk`, `/api/dashboard`, `/api/settings`, `/api/health`).
- **Database Layer**: MongoDB Atlas cluster (with an in-memory `mongomock` fallback for local development and offline unit testing).
- **Machine Learning Core**:
  - Phase 4: Scikit-learn **Isolation Forest** transaction anomaly detection (`transaction_anomaly_detector.joblib`).
  - Phase 5: TF-IDF vectorizer + Logistic Regression scam communication classifier (`scam_classifier.joblib`).
  - Phase 6: Explainable **Risk Fusion Engine** correlating cross-signal temporal risk events into unified scores ($0-100$) and categorizations (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Emergency Escalation Layer (Phase 8/9)**: Multi-channel SMS and Voice alerts via Twilio (live integration kept safely disabled via `TWILIO_ENABLED=false`; offline simulation verified via `MockTwilioClient`).

---

## 2. Current Authentication Architecture

- **Protocol**: Stateless JSON Web Tokens (JWT) adhering to RFC 7519.
- **Identities**: Users register under either the `ELDER` or `CAREGIVER` role.
- **Passwords**: Hashed with Werkzeug's salted password hashing algorithm (`scrypt`/`pbkdf2`). Plaintext passwords and hashes are never stored in memory or persisted in unhashed form.
- **Token Dual-Layer**:
  - `access_token`: Short-lived (default 900–3600 seconds) Bearer token required for all protected endpoints via `@jwt_required()`.
  - `refresh_token`: Long-lived (default 7 days) token used exclusively at `/api/auth/refresh` to grant new access tokens without requiring re-entry of credentials.

---

## 3. JWT Handling

- **Algorithm**: Standardized strictly on `HS256`.
- **Secret Key**: Sourced exclusively from `JWT_SECRET_KEY` in environment variables. Default development keys trigger explicit production rejection if deployed without configuration.
- **Claims**: Strictly minimal token payload:
  - `sub`: User ID
  - `user_id`: User identifier
  - `role`: Role string (`ELDER` or `CAREGIVER`)
  - `email`: Normalized email
  - `jti`: Unique UUIDv4 token identifier
  - `type`: Explicit token type discriminator (`access` vs `refresh`)
  - `iat`: Timestamp issued
  - `exp`: Timestamp of expiration
- **Revocation / Token Blacklist**: Revoked token JTIs are recorded in the `revoked_tokens` collection with BSON UTC timestamps. MongoDB automatically cleans up expired entries via a TTL index (`expireAfterSeconds=0`).
- **Deactivated Accounts**: Token verification directly validates active user status (`is_active: true`) on protected requests, guaranteeing deactivated accounts cannot execute actions even with unexpired tokens.

---

## 4. MongoDB Configuration

- **Connection**: Driven solely by `MONGODB_URI` environment variable.
- **Database Selection**: Configurable via `MONGODB_DATABASE`.
- **Resilience**: Client uses explicit timeouts:
  - `serverSelectionTimeoutMS=4000`
  - `connectTimeoutMS=4000`
- **Fallback**: In development and testing modes, automatically activates `mongomock` if `MONGODB_URI` is unset.
- **Indexes**: Nine production indexes verified on application launch:
  1. `users`: Unique `user_id`, unique `email`, sparse `phone`
  2. `transactions`: Unique `id`, compound `(user_id, timestamp desc)`, `status`, `payee`
  3. `alerts`: Unique `id`, `user_id`, `level`, `status`
  4. `analyzed_messages`: `user_id`, `analyzed_at`, `type`
  5. `risk_events`: `user_id`, `timestamp`
  6. `caregivers`: Unique `caregiver_id`, `elder_user_id`, `caregiver_user_id`, `is_active`
  7. `notification_preferences`: Unique `user_id`
  8. `notifications`: Unique `notification_id`, `user_id`, `caregiver_id`, `risk_event_id`, `transaction_id`, `created_at`
  9. `revoked_tokens`: Unique `jti`, TTL index on `expires_at` (`expireAfterSeconds=0`)

---

## 5. Twilio Configuration

- **Safety Default**: `TWILIO_ENABLED=false` is enforced as the default baseline. Real SMS/call dispatches cannot occur accidentally.
- **Backend Isolation**: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_FROM_PHONE` are strictly backend-only variables. They are never exposed to the client or returned in API responses.
- **Mock Provider**: `MockTwilioClient` records dispatches in-memory with unique mock SIDs (`SM_MOCK_*`, `CA_MOCK_*`) for comprehensive testing without billing or telecom activity.
- **Deduplication & Quiet Hours**: Idempotency and quiet-hours policies ensure caregivers are not spammed and emergency bypasses only trigger on `CRITICAL` risk events.

---

## 6. CORS Configuration

- **Development**: Permits `localhost` and `127.0.0.1` on ports 3000 and 5173.
- **Production**: Configurable via comma-separated `CORS_ORIGINS`. Wildcards (`*`) with credentials (`supports_credentials=True`) are prohibited for production security.
- **Headers**: Allowed request headers restricted to standard authorization and content negotiation headers.

---

## 7. Frontend Environment Configuration

- **Configuration File**: Controlled via `.env` and `import.meta.env`.
- **Variables**:
  - `VITE_API_BASE_URL`: URL to backend Flask service (`/api`).
  - `VITE_USE_MOCK_API`: Boolean switch for standalone frontend mock mode versus live API integration.
- **Auditing Result**: Zero secrets, private API keys, or database credentials exist in frontend code or build assets.

---

## 8. Backend Environment Configuration

- **Configuration Files**: `.env`, `.env.example`, `.env.production.example`.
- **Mode Separation**:
  - `DevelopmentConfig`: Debug enabled, auto-mock DB fallback when URI is empty.
  - `TestingConfig`: Isolated in-memory DB, rate limits relaxed for fast tests.
  - `ProductionConfig`: Debug disabled, strict DB requirements, HSTS enabled, strict CORS.

---

## 9. Secret Handling

- **Scan Finding**: 0 secrets discovered across the entire repository.
- **Protection**: `.gitignore` explicitly excludes `.env`, `.env.*`, and `.env.local` across all root and subdirectories.
- **Examples**: Clean example templates with placeholder values (`CHANGE_ME_IN_PRODUCTION`) provided for documentation and onboarding.

---

## 10. API Exposure

- **Public Endpoints**:
  - `GET /api/health`: Health probe (returns sanitized status without internal connection strings).
  - `POST /api/auth/register`: User registration with strict payload validation.
  - `POST /api/auth/login`: User authentication with generic error messages.
  - `POST /api/auth/refresh`: Token refresh with type validation.
  - `POST /api/notifications/webhook`: Provider delivery receipt callback.
- **Protected Endpoints**:
  - `POST /api/auth/logout`: Revokes active token.
  - `GET /api/auth/me`: Retrieves authenticated user profile.
  - `GET /api/caregivers`: Lists verified caregivers for the authenticated elder.
  - `POST /api/caregivers`: Registers new caregiver under the elder's ownership.
  - `PATCH /api/caregivers/<id>`: Updates caregiver preferences/status.
  - `DELETE /api/caregivers/<id>`: Removes caregiver association.
  - `GET /api/notifications`: Retrieves notifications with ownership isolation.
  - `POST /api/notifications/<id>/acknowledge`: Emergency acknowledgement with authorization check.
  - `POST /api/notifications/escalate`: Triggers rate-limited manual risk escalation.
  - `POST /api/analyze-transaction`: Behavioral anomaly detection.
  - `POST /api/analyze-message`: NLP communication analysis.
  - `POST /api/risk/analyze`: Multi-signal Risk Fusion Engine.

---

## 11. Input Validation

- **Boundary Enforcement**:
  - Transaction Amount: Positive, finite float capped at ₹10,000,000 (1 Crore INR UPI limit).
  - Payee Name: String capped at 200 characters.
  - UPI ID: String capped at 100 characters.
  - Message Text: String capped at 5,000 characters to prevent memory exhaustion.
  - User Names: Minimum 2 characters, maximum 100 characters.
  - Passwords: Minimum 8 characters, maximum 128 characters, requires both letters and numbers.
- **Malformed Inputs**: Unexpected types, missing required fields, or non-finite numbers return structured HTTP 400 `ValidationError` responses.

---

## 12. Error Handling

- **Centralized Error Handlers**:
  - Custom exceptions (`AppError`, `ValidationError`, `NotFoundError`, `UnauthorizedError`, `ForbiddenError`, `ConflictError`, `ModelNotAvailableError`) serialize to standardized JSON: `{"error": "<message>", "status": <code>}`.
  - Unhandled 500 exceptions and generic `Exception` handlers catch server errors, log tracebacks internally, and return sanitized `{"error": "Internal server error", "status": 500}`.
- **Zero Leakage**: Internal file paths, Python tracebacks, database URI strings, and JWT secrets are never exposed in error payloads.

---

## 13. Logging

- **Policy**: Structured application logging at configurable `LOG_LEVEL` (default `INFO`).
- **Sanitization**:
  - Passwords and password hashes are never logged.
  - JWT tokens and refresh tokens are excluded from log outputs.
  - Phone numbers are masked (e.g. `+919876****`).
  - SMS/Call transcripts: Only metadata (length, timestamp, risk score) is logged; full sensitive financial messages are not dumped into server logs.
  - Twilio Webhook: Only SID and status are logged.

---

## 14. Rate Limiting

- **Implementation**: Sliding-window thread-safe rate limiter (`app/utils/rate_limiter.py`).
- **Enforced Routes**:
  - `POST /api/auth/register`: 10 requests / minute / IP
  - `POST /api/auth/login`: 15 requests / minute / IP
  - `POST /api/auth/refresh`: 30 requests / minute / IP
  - `POST /api/notifications/escalate`: 20 requests / minute / client
- **Response**: Exceeding rate limit returns HTTP 429 `Too Many Requests` with `Retry-After` header.

---

## 15. Notification Safety

- **Default State**: Inactive (`TWILIO_ENABLED=false`).
- **Deduplication**: Notifications for identical risk events and caregiver channels are deduplicated within sliding time windows.
- **Caregiver Rate Limiting**: Maximum 3 notifications per caregiver per hour to prevent notification exhaustion.
- **Quiet Hours**: Non-critical notifications are suppressed during quiet hours (10:00 PM – 7:00 AM); critical risk events bypass quiet hours safely.

---

## 16. File Upload Risks

- **Audit Result**: UPI Guardian does not accept binary file uploads or multipart form file inputs. Analysis operates strictly on structured JSON payloads.
- **Risk Rating**: **NONE / NOT APPLICABLE**.

---

## 17. Dependency Risks

- **Backend**: Standard dependencies locked with semantic ranges in `requirements.txt`:
  - Flask 3.0, Werkzeug 3.0, PyJWT 2.8, scikit-learn 1.4, pandas 2.2, pymongo 4.6, gunicorn 21.2.
- **Frontend**: Vite 8.1, React 19.2, TanStack Start/Router, Radix UI primitives.
- **Audit Result**: No deprecated or abandoned critical packages identified.

---

## 18. Accessibility Status

- **Evaluation Standard**: Internal WCAG 2.1 AA evaluation.
- **Senior Mode**: High-visibility toggle with 112% base font scaling, minimum 48px touch targets, OKLCH contrast-enhanced color palettes, and clear plain-language risk alerts.
- **Keyboard Access**: Modal dialogs, notifications drawer, and mobile menu all support full keyboard navigation and close via the `Escape` key.
- **Reduced Motion**: Respects `prefers-reduced-motion` media queries by collapsing animation durations.

---

## 19. Deployment Readiness

- **Containerization**:
  - `backend/Dockerfile`: Multi-stage Python 3.11 slim image running Gunicorn as a non-privileged `appuser`.
  - `frontend-magic-wand-07-main/Dockerfile`: Multi-stage Node 20 alpine build serving static production bundle via non-root `node` user.
  - `docker-compose.yml`: Configured for local development and integration verification.
- **Configuration Templates**: Complete `.env.production.example` files provided for both backend and frontend.

---

## 20. Known Remaining Risks & Phase 10 Roadmap

1. **In-Memory Rate Limiting vs Distributed Cache**: Current sliding-window rate limiter runs in-process. For horizontally scaled multi-worker cloud deployments in Phase 10, an external Redis or Cloudflare/NGINX edge rate limiter is recommended.
2. **Twilio Webhook Live Signature Verification**: Placeholder webhook endpoint is prepared and functional. Live `X-Twilio-Signature` cryptographic validation requires active Twilio auth token and HTTPS webhook URL registration in the Twilio Console (scheduled for Phase 10).
3. **Atlas Network Access**: Production Atlas database must configure strict IP allowlists or VPC peering rather than universal access (`0.0.0.0/0`).
4. **Cloud Infrastructure**: Final cloud hosting (Render, Vercel, or AWS) is intentionally reserved for Phase 10.
