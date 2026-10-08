# UPI Guardian — Phase 7: Frontend ↔ Backend Full Integration

This document details the end-to-end integration between the **React/TanStack Start/Vite frontend** (`frontend-magic-wand-07-main/`) and the **Flask REST API backend with MongoDB Atlas, Isolation Forest ML, NLP Scam Classifier, and Phase 6 Risk Fusion Engine** (`backend/`).

---

## 1. Frontend Architecture

The frontend is built using:
- **Framework**: TanStack Start with Vite + React 19.
- **Routing**: TanStack Router (file-based in `src/routes/`).
- **Server State Management**: TanStack Query (`@tanstack/react-query` v5).
- **Design System & Styling**: Tailored CSS design tokens with support for Dark/Light mode and accessibility features (Senior Mode, Reduced Motion).
- **Data Visualization**: Recharts (PieChart, BarChart, LineChart) and custom SVG components (`RiskGauge`).

The data flow is structured as:
```text
UI Page Components (pages.tsx, app-shell.tsx)
          ↓
TanStack Query Hooks (useTransactions, useRiskAnalysis, etc.)
          ↓
Centralized API Service Layer (transaction-service.ts, risk-service.ts, etc.)
          ↓
HTTP Client (api-client.ts) [Configurable Mock Fallback / Real Flask REST]
          ↓
Flask REST API (http://127.0.0.1:5000/api)
          ↓
Inference Services (Risk Fusion Engine, NLP Classifier, ML Isolation Forest)
          ↓
MongoDB Atlas Collections / Repositories
```

---

## 2. API Service Layer

All external communications pass through dedicated service modules located in `src/services/`:

1. **`api-client.ts`**:
   - Centralized Axios-like wrapper over `fetch`.
   - Normalizes base URL path (guarantees `/api` suffix is applied consistently).
   - Formats network and backend error payloads into human-readable error messages (`"Unable to connect to UPI Guardian server."`).
   - Exports `isMockEnabled()` boolean helper governed by `VITE_USE_MOCK_API`.

2. **`health-service.ts`**:
   - Manages `GET /api/health` connectivity polling and service telemetry.

3. **`dashboard-service.ts`**:
   - Calls `GET /api/dashboard/summary` to retrieve aggregated KPIs, system status, active alerts, and cross-signal correlation counts.

4. **`transaction-service.ts`**:
   - Calls `GET /api/transactions` (with query filtering for payee/status).
   - Calls `GET /api/transactions/:id` for specific transaction inspection.
   - Calls `POST /api/analyze-transaction` for standalone behavioral anomaly detection.
   - Normalizes backend documents into the strict `Transaction` interface.

5. **`risk-service.ts`**:
   - Calls `POST /api/risk/analyze` to execute the Phase 6 Risk Fusion Engine.
   - Calls `GET /api/risk/events` to fetch historical multi-signal audit log entries.

6. **`message-service.ts`**:
   - Calls `POST /api/analyze-message` for real-time NLP classification of SMS messages (`message_type="sms"`) and call transcripts (`message_type="call_transcript"`).

7. **`alert-service.ts`**:
   - Calls `GET /api/alerts` to list pending/flagged security alerts.
   - Calls `POST /api/alerts/:id/resolve` to transition alerts to `"resolved"`.

8. **`family-service.ts`**:
   - Calls `GET /api/family/profile` for elder profile and active risk counts.
   - Calls `POST /api/family/alerts/resolve` to resolve family-facing warnings.

9. **`settings-service.ts`**:
   - Calls `GET /api/settings` to load profile, security, and alert preferences.
   - Calls `PATCH /api/settings` to persist updates into the database.

---

## 3. Environment Variables

Configuration is handled cleanly via environment files in `frontend-magic-wand-07-main/`:

| Variable | Description | Example (Development) |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Base URL of the Flask API backend | `http://127.0.0.1:5000/api` |
| `VITE_USE_MOCK_API` | Flag to enable synthetic mock data mode | `false` (real API) / `true` (mock) |

### Frontend Security Boundary
The frontend environment strictly contains public configuration.
It **NEVER** contains:
- MongoDB URI strings or Atlas credentials.
- Backend secret keys or signing keys.
- Twilio Account SIDs or Auth Tokens (reserved for Phase 8 backend).

---

## 4. Mock Mode vs. Real API Mode

### Mock Mode (`VITE_USE_MOCK_API=true`)
- Serves synthetic offline data from `src/services/mock-provider.ts` and `src/data/mock/`.
- Enables demonstration and UI prototyping without requiring a running Flask server or MongoDB Atlas connection.
- Explicitly flags simulated responses with `isDemo: true`.

### Real API Mode (`VITE_USE_MOCK_API=false`)
- Directs all requests to the Flask backend over HTTP.
- Does **NOT** silently mask backend downtime with fake success data.
- Surfaces clear, contextual error states if the backend is unreachable or returns an error.

---

## 5. Endpoint Mapping

| Frontend Feature | HTTP Method | Flask Route | Backend Service |
| :--- | :--- | :--- | :--- |
| System Health | `GET` | `/api/health` | Health Check Route |
| Dashboard Summary | `GET` | `/api/dashboard/summary` | `DashboardService` |
| Transaction List | `GET` | `/api/transactions` | `TransactionService` / `TransactionRepository` |
| Transaction Detail | `GET` | `/api/transactions/<id>` | `TransactionService` / `TransactionRepository` |
| Behavioral Anomaly | `POST` | `/api/analyze-transaction` | `AnomalyDetectionService` (Isolation Forest) |
| SMS Scam Detection | `POST` | `/api/analyze-message` | `NLPScamDetectionService` (TF-IDF + LogReg) |
| Call Transcript Scam | `POST` | `/api/analyze-message` | `NLPScamDetectionService` (TF-IDF + LogReg) |
| Risk Fusion Analysis | `POST` | `/api/risk/analyze` | `RiskFusionService` (Phase 6 Fusion Engine) |
| Risk Events Audit | `GET` | `/api/risk/events` | `RiskEventRepository` |
| Alerts List | `GET` | `/api/alerts` | `AlertRepository` |
| Resolve Alert | `POST` | `/api/alerts/<id>/resolve` | `AlertRepository` |
| Family Profile | `GET` | `/api/family/profile` | `FamilyService` / `UserRepository` |
| Family Alerts Resolve| `POST` | `/api/family/alerts/resolve`| `FamilyService` / `AlertRepository` |
| Get User Settings | `GET` | `/api/settings` | `SettingsService` / `SettingsRepository` |
| Update User Settings | `PATCH` | `/api/settings` | `SettingsService` / `SettingsRepository` |

---

## 6. Query Hooks & State Management

Centralized custom hooks in `src/hooks/`:

- **`useHealthCheck()`**: Periodic background health ping (60s stale time) displayed in the sidebar connectivity badge.
- **`useDashboard()`**: Fetches live metrics for the dashboard page.
- **`useTransactions(filters)`**: Manages transaction list filtering by risk status and search terms.
- **`useTransaction(id)`**: Fetches a specific transaction for modal review.
- **`useAlerts(status)`**: Retrieves alerts filtered by severity.
- **`useResolveAlert()`**: Mutates alert state and invalidates `['alerts']` and `['dashboard']` caches.
- **`useAnalyzeMessage()`**: Triggers NLP analysis on SMS/calls.
- **`useRiskAnalysis()`**: Executes Phase 6 multi-signal composite fusion, invalidating risk and dashboard queries on completion.
- **`useRiskEvents()`**: Loads historical fusion events for audit trails.
- **`useFamily()`**: Reads elder telemetry and caregiver contacts.
- **`useSettings()` / `useUpdateSettings()`**: Reads and partially updates user preferences.

---

## 7. Loading, Error, and Empty States

Every integrated page implements comprehensive state handling:

1. **Loading State**:
   - Uses non-blocking animated spinners (`<RefreshCw className="animate-spin" />`) and loading skeletons.
   - Prevents UI freezing during ML and NLP inference calls.

2. **Error State**:
   - Renders polished danger-toned cards with retry buttons (`refetch()`).
   - Replaces technical stack traces with clear, user-friendly language:
     - `"Unable to connect to UPI Guardian server."`
     - `"Failed to load transaction records."`
     - `"Risk analysis could not be completed. Please try again."`

3. **Empty State**:
   - Polished empty-state cards when collections contain 0 records:
     - Transactions: `"No suspicious transactions found. Your account looks safe."`
     - Alerts: `"No active alerts. Everything is currently safe."`

---

## 8. CORS Configuration

The Flask application factory (`backend/app/__init__.py`) initializes Flask-CORS with:
- Resources scoped to `/api/*`.
- Configurable origins via `CORS_ORIGINS` environment variable (defaults to `http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000`).
- Credentials supported (`supports_credentials=True`).
- Production configurations restrict wildcards (`*`) to explicit allowed origins.

---

## 9. Risk Fusion Integration (Phase 6)

The **Explainable Risk Analysis** page (`/risk-analysis`) connects directly to `POST /api/risk/analyze`.

### Visualized Outputs:
- **Combined Risk Score**: 0–100 score displayed via circular `RiskGauge`.
- **Risk Level**: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL` badge.
- **Full Signal Breakdown**:
  - Transaction Anomaly Score (0–100)
  - Communication Risk Score (0–100)
  - Behavioral Deviation Score (0–100)
  - New Payee Score (0 or 100)
  - Velocity Score (0–100)
  - Temporal Correlation Score (0–100)
  - Correlation Boost (`+X.X` boost badge when signals correlate within the 2-hour window)
- **Pipeline Formula**: Displays the multi-signal composition equation.
- **Contributing Factors & Explanation**: Natural language breakdown generated by the fusion engine.
- **Actionable Guidance**: Elder-safe recommended actions.
- **Audit Timeline**: Live audit records fetched from `GET /api/risk/events`.

---

## 10. SMS and Call Transcript Scam Detection (Phase 5)

Both the **SMS Scam Detector** (`/sms-analyzer`) and **Call Analyzer** (`/call-analyzer`) connect to `POST /api/analyze-message`:

- **Input**: Raw text message or call transcript.
- **Output**:
  - Risk score (0–100) and severity level badge.
  - Detected scam categories (e.g. `Otp Request`, `Urgency Or Threat`, `Account Blocking Claim`).
  - Identified suspicious phrases extracted by the NLP analyzer.
  - Plain-language explanation.
  - Elder-safe safety recommendations.
- **Safety Terminology**: The UI strictly uses advisory language (`"Potential scam detected"`, `"Suspicious communication detected"`) and **never** makes definitive claims of `"Fraud confirmed"`.

---

## 11. Alerts and Resolution Workflow

The **Fraud Alerts** page (`/alerts`):
- Consumes real alert documents from `GET /api/alerts`.
- Supports filtering by severity (`critical`, `high`, `review`, `all`).
- Resolving an alert (`POST /api/alerts/<id>/resolve`) triggers immediate TanStack Query invalidation without requiring a page reload.

---

## 12. Family Safety Center & Boundary Definition

The **Family Safety Center** (`/family`):
- **Active Phase 7 Capabilities**:
  - Connects to `GET /api/family/profile` for Sunita Devi's real-time safety status.
  - Displays dynamic account metrics (`todayTransactionsCount`, `activeAlertsCount`, `currentRiskScore`).
- **Phase 8 Demarcation**:
  - Explicitly marked: Automated Twilio caregiver voice calls, emergency SMS alerts, and multi-user authentication are reserved for Phase 8.

---

## 13. Settings Persistence

The **Settings** page (`/settings`):
- Loads stored preferences via `GET /api/settings`.
- Allows updating profile details, security toggles (2FA, login activity alerts), alert preferences, and accessibility options.
- Persists changes to the MongoDB backend via `PATCH /api/settings`.

---

## 14. Senior Mode Preservation

Senior Mode remains fully supported:
- **Visuals**: Enhanced typography, larger touch targets, simplified layouts.
- **Explanations**: High-risk explanations emphasize immediate actions (e.g., *"Do not share your UPI PIN. Call a family member immediately."*) rather than raw statistical algorithms.
- **Toggling**: Senior Mode can be switched seamlessly from any page via the header toggle or the Settings page.

---

## 15. Local Development Instructions

### Starting the Flask Backend
```powershell
cd "backend"
# Ensure virtual environment is activated
python run.py
# Backend starts at http://127.0.0.1:5000
```

### Starting the React Frontend (Real API Mode)
```powershell
cd "frontend-magic-wand-07-main"
# Ensure .env has:
# VITE_API_BASE_URL=http://127.0.0.1:5000/api
# VITE_USE_MOCK_API=false

npm run dev
# Frontend starts at http://localhost:5173
```

### Running in Mock Demo Mode
In `frontend-magic-wand-07-main/.env`:
```ini
VITE_USE_MOCK_API=true
```

---

## 16. Verification & Test Results

1. **Backend Test Suite**:
   ```bash
   pytest -q
   # Result: 122 passed in 2.10s (100% pass rate)
   ```
2. **Phase 7 Full E2E Verification Script**:
   ```bash
   python backend/scripts/verify_phase7_integration.py
   # Result: All 11 endpoint flows passed with 100% success
   ```
3. **Frontend TypeScript Check**:
   ```bash
   npx tsc --noEmit
   # Result: 0 errors
   ```
4. **Frontend Production Build**:
   ```bash
   npm run build
   # Result: Exit code 0 (Vite SSR + Nitro build successful)
   ```

---

## 17. Scope Confirmation

The following features were **STRICTLY EXCLUDED** from Phase 7:
- Twilio SMS / Voice integration.
- Caregiver emergency voice calling.
- Authentication, JWT, and user login/signup.
- WebSockets for real-time pushing.
- Deployment to Vercel, Render, or cloud infrastructure.
These components belong to Phase 8 and subsequent development phases.
