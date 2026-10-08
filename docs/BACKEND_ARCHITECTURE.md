# UPI Guardian - Backend Architecture Specification

> **Document Version:** 1.0  
> **Phase:** Phase 2 Backend Scaffolding & Core Flask REST API  
> **Date:** October 8, 2026  

---

## 1. Architectural Overview

The **UPI Guardian** backend is architected as a lightweight, modular **Python Flask REST API** service designed for real-time transaction scoring, explainable threat aggregation, caregiver notifications, and scam communication analysis.

```
                      ┌───────────────────────────────────────┐
                      │    React 19 Frontend (Port 3000)      │
                      └──────────────────┬────────────────────┘
                                         │ (HTTP JSON / CORS)
                                         ▼
                      ┌───────────────────────────────────────┐
                      │          Flask Application            │
                      │    (create_app Application Factory)   │
                      └──────────────────┬────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │                                │                                │
        ▼                                ▼                                ▼
┌─────────────────┐            ┌──────────────────┐             ┌─────────────────┐
│ Modular Routes  │            │  Centralized     │             │ Request Schemas │
│  & Blueprints   │            │  Error Handlers  │             │  & Validation   │
│  (/api/*)       │            │  (400, 404, 500) │             │ (schemas/*)     │
└───────┬─────────┘            └──────────────────┘             └─────────────────┘
        │
        ▼
┌─────────────────┐
│ Service Layer   │
│ (services/*)    │
└───────┬─────────┘
        │
        ▼
┌─────────────────┐
│ Data Layer /    │
│ Domain Models   │
│ (models/*)      │
└─────────────────┘
```

---

## 2. Directory Layout

```
backend/
├── app/
│   ├── __init__.py           # Flask application factory (create_app)
│   ├── config.py             # Config, DevelopmentConfig, TestingConfig, ProductionConfig
│   ├── extensions.py         # CORS extension initialization
│   ├── routes/               # Modular REST Blueprints
│   │   ├── __init__.py       # Blueprint registry
│   │   ├── health.py         # GET /api/health
│   │   ├── dashboard.py      # GET /api/dashboard/summary
│   │   ├── transactions.py   # GET, POST /api/transactions, /api/analyze-transaction
│   │   ├── alerts.py         # GET, POST /api/alerts, /api/alerts/<id>/resolve
│   │   ├── family.py         # GET, POST /api/family/profile, /api/family/alerts/resolve
│   │   ├── messages.py       # POST /api/analyze-message
│   │   └── settings.py       # GET, PATCH /api/settings
│   ├── services/             # Business logic layer
│   │   ├── transaction_service.py
│   │   ├── dashboard_service.py
│   │   ├── alert_service.py
│   │   ├── family_service.py
│   │   ├── message_service.py
│   │   └── settings_service.py
│   ├── models/               # Data models and synthetic in-memory repositories
│   │   ├── transaction.py
│   │   ├── alert.py
│   │   ├── elder_profile.py
│   │   └── settings.py
│   ├── schemas/              # Request payload validation
│   │   └── validators.py
│   └── utils/                # Centralized errors and response helpers
│       ├── errors.py         # AppError, ValidationError, NotFoundError
│       └── responses.py      # json_response helper
├── tests/                    # Pytest test suite
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_dashboard.py
│   ├── test_transactions.py
│   ├── test_alerts.py
│   ├── test_family.py
│   ├── test_messages.py
│   ├── test_settings.py
│   └── test_errors.py
├── requirements.txt          # Python dependencies
├── run.py                    # Server runner
├── .env.example              # Environment variables template
└── README.md                 # Backend documentation
```

---

## 3. Core Architectural Patterns

### 3.1 Application Factory (`create_app`)
The application is constructed via `create_app(config_name=None)` in `app/__init__.py`. This enables:
- Dynamic configuration swapping between `development`, `testing`, and `production`.
- Clean isolation for unit and integration testing under `pytest`.
- Extension initialization without circular imports.

### 3.2 Modular Blueprints
All HTTP endpoints are grouped into dedicated Blueprints mounted under the common prefix `/api`:
- `health_bp`: Liveness and readiness probes.
- `dashboard_bp`: Overview KPIs and risk gauges.
- `transactions_bp`: Transaction monitoring and anomaly evaluation.
- `alerts_bp`: Prioritized fraud warnings and caregiver clearance.
- `family_bp`: Elder safety profile and family notifications.
- `messages_bp`: SMS and call transcript NLP analysis.
- `settings_bp`: User preferences and accessibility configuration.

### 3.3 Decoupled Service Layer
Route handlers are thin controllers responsible only for deserialization, validation, calling the service layer, and returning standard JSON. Business rules and data mutations are strictly confined to `app/services/`.

### 3.4 Strict Policy on Development Stubs
In accordance with phase requirements:
- No fake ML/AI predictions are returned.
- Initial endpoints that will later connect to machine learning models (Isolation Forest in Phase 3, NLP in Phase 4) return explicitly marked development stubs with `"isDevelopmentStub": true`.

### 3.5 Centralized Error Handling
The application defines custom exception classes deriving from `AppError`:
- `ValidationError` (HTTP 400)
- `NotFoundError` (HTTP 404)
- Standard handlers for HTTP 400, 404, 405, and 500 guarantee uniform JSON error envelopes:
```json
{
  "error": "Error description message",
  "status": 400
}
```

### 3.6 Cross-Origin Resource Sharing (CORS)
Configured using `Flask-CORS` in `app/extensions.py`. The allowed origins are configurable through `CORS_ORIGINS` in `.env`, allowing seamless interaction with Vite/React on `http://localhost:3000` or `http://localhost:5173`.
