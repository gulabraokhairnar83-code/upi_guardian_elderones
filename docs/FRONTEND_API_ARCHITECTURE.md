# UPI Guardian - Frontend API Architecture & Service Layer

> **Document Version:** 1.0  
> **Date:** October 8, 2026  
> **Scope:** Phase 1 Frontend API Service Layer, Mock Repositories, TanStack Query Hooks, and Flask Backend Integration Protocol.

---

## 1. Overview & Architecture Design

The UPI Guardian frontend connects to a decoupled service abstraction layer designed for high-concurrency fraud detection, transaction telemetry, explainable risk calculations, and scam communications analysis. 

During **Phase 1**, all UI views consume services through **TanStack Query hooks** backed by a plug-and-play **Mock Provider** containing synthetic banking datasets. This allows instant frontend functionality while strictly preparing standardized REST contracts for the future **Python/Flask** backend.

```
┌─────────────────────────────────────────────────────────────┐
│                 React 19 Presentation Layer                 │
│  (Dashboard, Transactions, Alerts, Analyzers, Family, etc.) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    TanStack Query Hooks                     │
│  (useDashboard, useTransactions, useAlerts, useFamily, etc.)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer (Typed)                   │
│ (dashboard-service, transaction-service, alert-service, etc)│
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
        (VITE_USE_MOCK_API=false)       (VITE_USE_MOCK_API=true / Fallback)
               ▼                               ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│       HTTP API Client        │ │        Mock Provider        │
│  - Centralized Base URL      │ │  - Realistic async latency  │
│  - JSON parsing & timeouts   │ │  - Centralized repositories │
│  - Network error handling    │ │  - Flagged demo markers     │
└──────────────┬───────────────┘ └─────────────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Future Flask REST API    │
│  (Isolation Forest, NLP ML)  │
└──────────────────────────────┘
```

---

## 2. Environment Variables & Centralized Configuration

All environment configurations are managed via `.env` with fallback defaults.

### `.env.example`
```bash
# UPI Guardian - Environment Configuration Template
# Base URL for future Flask REST API backend
VITE_API_BASE_URL=http://localhost:5000/api

# Enable mock API provider during frontend development (true / false)
VITE_USE_MOCK_API=true
```

- **`VITE_API_BASE_URL`**: Specifies the Flask API gateway location (defaults to `http://localhost:5000/api`).
- **`VITE_USE_MOCK_API`**: When set to `true`, queries and mutations are routed to `mockProvider`. When set to `false`, requests are dispatched to Flask via `apiClient`. If the backend is offline during development, the service layer automatically falls back to `mockProvider` without breaking page UI.

TypeScript types are augmented in `src/vite-env.d.ts` ensuring strict compatibility with `noPropertyAccessFromIndexSignature`.

---

## 3. Centralized API Client (`src/services/api-client.ts`)

The centralized `ApiClient` class wraps native `fetch` with robust production safeguards:

- **Configurable Base URL:** Standardizes endpoint paths and query string formatting.
- **Strict JSON Parsing:** Automatically inspects `Content-Type`, parses JSON payloads, and handles empty responses.
- **Request Timeout:** Features configurable request abortion via `AbortController` (default 10,000ms).
- **Custom Typed Errors (`ApiClientError`):** Captures HTTP status code, status text, server error message payloads, and flags network connection failures and timeouts.
- **Security:** Exposes no credentials, tokens, or hardcoded secrets.

```ts
export class ApiClientError extends Error {
  public readonly status: number;
  public readonly statusText: string;
  public readonly data: unknown;
  public readonly isNetworkError: boolean;
  public readonly isTimeout: boolean;
}
```

---

## 4. Service Layer Specifications

Located under `src/services/`:

| Service | Primary Operations | Target Flask Endpoint | Payload / Response |
| :--- | :--- | :--- | :--- |
| **`dashboard-service.ts`** | `getSummary()` | `GET /api/dashboard/summary` | Returns KPI statistics, recent activity, system status, and current risk. |
| **`transaction-service.ts`** | `getTransactions()`<br>`getTransactionById(id)`<br>`analyzeTransaction(payload)` | `GET /api/transactions`<br>`GET /api/transactions/:id`<br>`POST /api/analyze-transaction` | Queries synthetic UPI list; posts transaction factors for Isolation Forest scoring. |
| **`alert-service.ts`** | `getAlerts(level)`<br>`resolveAlert(id)` | `GET /api/alerts`<br>`POST /api/alerts/:id/resolve` | Queries prioritized alerts; updates alert status. |
| **`message-service.ts`** | `analyzeMessage(payload)`<br>`getSampleMessage(type)` | `POST /api/analyze-message` | Submits SMS / phone transcript to NLP engine for scam pattern extraction. |
| **`family-service.ts`** | `getElderProfile()`<br>`getEmergencyContacts()`<br>`resolveFamilyAlert()` | `GET /api/family/profile`<br>`GET /api/family/contacts`<br>`POST /api/family/alerts/resolve` | Elder status tracking and caregiver alert notifications. |
| **`settings-service.ts`** | `getSettings()`<br>`updateSettings(data)` | `GET /api/settings`<br>`PATCH /api/settings` | User preferences, senior mode, and alert switches. |
| **`auth-service.ts`** | `getCurrentUser()`<br>`logout()` | `GET /api/auth/me`<br>`POST /api/auth/logout` | Session verification and logout actions. |

---

## 5. TanStack React Query Hooks

Located under `src/hooks/`:

- **`useDashboard()`**: Caches dashboard overview with 30s stale time.
- **`useTransactions(filter)`**: Reactively fetches transactions by status and search substring.
- **`useTransaction(id)`**: Fetches detailed view for individual transaction modals.
- **`useAnalyzeTransaction()`**: Mutation for triggering real-time ML anomaly checks.
- **`useAlerts(level)`**: Queries alerts filtered by severity.
- **`useResolveAlert()`**: Mutation to mark alerts resolved, automatically invalidating alert cache.
- **`useAnalyzeMessage()`**: Mutation for SMS & Call analyzers, outputting risk score and pattern checklist.
- **`useFamily()`**: Composite hook bundling elder profile and emergency contact queries.
- **`useResolveFamilyAlert()`**: Caregiver mutation clearing urgent active payment warnings.
- **`useSettings()` / `useUpdateSettings()`**: Preferences synchronization.

---

## 6. Mock Data Provider (`src/services/mock-provider.ts`)

To avoid scattered inline arrays across JSX files, mock repositories have been centralized in `src/data/mock/`:

- `elder-profile.ts`: "Sunita Devi" demographic and account safety profile.
- `emergency-contacts.ts`: Family contacts (Rajesh Devi, Kavita Rao, Dr. Mehta).
- `sample-messages.ts`: Pre-filled scam prompts and pattern checklists.
- `incident-timeline.ts`: Chronological threat development with typed Lucide icon components.
- `transactions.ts`: 24 synthetic UPI transactions with strict index bounds checks.
- `alerts.ts`: 3 prioritized fraud alerts.

### Demo Marker Policy
Mock analyzer responses are explicitly annotated with `isDemo: true` and "Demo Pattern Analysis" labels. The frontend never misrepresents static synthetic outputs as real ML predictions.

---

## 7. Error, Loading, and Empty States

Every page handling asynchronous server state implements four UI states adhering to the UPI Guardian design system:

1. **Loading State:** Subtle non-blocking spinner or indicator preserving layout stability without layout shift.
2. **Success State:** Interactive data presentation with OKLCH theme colors and SVG graphs.
3. **Empty State:** Styled `.empty-state` container with `CheckCircle2` icon and reassuring confirmation message ("Your account looks safe.").
4. **Error / Network Failure State:** Styled inline card or alert banner displaying actionable messages with an immediate "Retry" trigger.

---

## 8. Migration to Flask Backend (Phase 2 Roadmap)

When Flask is mounted in Phase 2:
1. Launch Flask REST server at `http://localhost:5000`.
2. Update `.env` to `VITE_USE_MOCK_API=false`.
3. The frontend components require **zero alterations** because they communicate solely through the service contracts.
