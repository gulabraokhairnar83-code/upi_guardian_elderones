# UPI Guardian — System Architecture Specification

**Project**: UPI Guardian  
**Phase**: Phase 10 (Final Project Release)  
**System Type**: Explainable AI-Assisted Early-Warning & Caregiver Safety Network  
**Target Users**: Senior Citizens (Elders) & Nominated Family Caregivers  

---

## 1. Architectural Philosophy & Safety Disclaimer

UPI Guardian is designed as an **early-warning risk assessment and caregiver safety layer**. 

> [!IMPORTANT]  
> - **Risk Signal Generation**: Machine learning and NLP models generate probabilistic risk indicators.
> - **Signal Fusion**: The Risk Fusion Engine combines multiple distinct signals (behavioral anomaly, text scam patterns, payee novelty, transaction velocity, and temporal correlation).
> - **Advisory Scope**: The system provides an **automated risk warning** to prompt secondary human verification. It **DOES NOT** claim to confirm fraud, freeze bank accounts, or interface directly with internal NPCI banking switches.

---

## 2. End-to-End Conceptual Flow

```
                                  User / Elder
                                       │
                                       ▼
                       React 19 Frontend (TanStack Start)
                        (Senior Mode / High Contrast UI)
                                       │
                                       │  JWT Bearer (HS256)
                                       ▼
                             Flask REST API Engine
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
          Authentication Service                Application APIs
             (JWT / Werkzeug)             (Transactions / Messages / Alerts)
                     │                                   │
                     │                                   │
                     ▼                                   ▼
             MongoDB Database ◄──────────────── Risk Fusion Engine
             (Atlas / mongomock)                         │
                                       ┌─────────────────┴─────────────────┐
                                       ▼                                   ▼
                             Isolation Forest                     NLP Scam Classifier
                            (Transaction Anomaly)                 (TF-IDF + Logistic Reg)
                                       │                                   │
                                       └─────────────────┬─────────────────┘
                                                         │
                                                         ▼
                                                Fused Risk Score
                                                 (0.0 to 100.0)
                                                         │
                                       ┌─────────────────┴─────────────────┐
                                       ▼                                   ▼
                                  LOW / MEDIUM                       HIGH / CRITICAL
                               (Advisory in App)                           │
                                                                           ▼
                                                                  Escalation Service
                                                                  (Caregiver Matching)
                                                                           │
                                                                           ▼
                                                                  Notification Policy
                                                             (Deduplication / Quiet Hours)
                                                                           │
                                                                           ▼
                                                                   Twilio Dispatcher
                                                                (SMS / Automated Voice)
```

---

## 3. Layer Breakdown

### Layer 1: Client Application (Frontend)
- **Technology**: React 19, TanStack Router / TanStack Start, Vite 8, Tailwind CSS v4, Lucide Icons.
- **Key Subsystems**:
  - **Senior Mode Engine**: Dynamically scales base text to $112\%$, enlarges interactive targets to $\ge 48\text{px}$, and enforces plain-language advisories.
  - **API Service Layer**: Dual-mode HTTP client supporting offline mock data demonstration (`VITE_USE_MOCK_API=true`) and live backend communication (`VITE_USE_MOCK_API=false`).
  - **Telemetry Dashboard**: Visualizes risk gauges, temporal trends, transaction histories, and active caregiver alerts.

### Layer 2: API Gateway & Application Server (Backend)
- **Technology**: Python 3.11, Flask 3.0, Gunicorn WSGI server.
- **Key Subsystems**:
  - **Authentication & Security Middleware**: HS256 JWT decoding, active account verification, sliding-window in-memory rate limiting, and HTTP security headers (`CSP`, `X-Frame-Options`, `nosniff`).
  - **Modular Blueprints**: Decoupled routes for `/auth`, `/caregivers`, `/notifications`, `/risk`, `/dashboard`, `/settings`, and `/health`.

### Layer 3: Machine Learning & NLP Analytics
- **Model 1: Transaction Anomaly Engine (Phase 4)**:
  - Algorithm: Scikit-learn **Isolation Forest** (`contamination=0.08`, `n_estimators=100`).
  - Inputs: Transaction amount, payee familiarity, velocity (frequency within 24 hours), time-of-day deviation, transaction type.
  - Output: Continuous decision anomaly score mapped to $0.0-1.0$.
- **Model 2: Scam Communication Analyzer (Phase 5)**:
  - Algorithm: **TF-IDF Vectorizer** (unigram + bigram, sublinear TF) + **Logistic Regression** (`C=1.5`, balanced class weighting).
  - Inputs: Inbound SMS text or digitized call transcript.
  - Output: Calibrated scam probability ($0.0-1.0$) and extracted scam keyword triggers.

### Layer 4: Explainable Risk Fusion Engine (Phase 6)
- **Fusion Formula**:
  $$\text{Fused Score} = (W_{\text{anomaly}} \cdot S_{\text{anomaly}}) + (W_{\text{nlp}} \cdot S_{\text{nlp}}) + (W_{\text{payee}} \cdot S_{\text{payee}}) + (W_{\text{velocity}} \cdot S_{\text{velocity}}) + C_{\text{temporal}}$$
- **Weights**:
  - Anomaly Score: $0.35$
  - NLP Scam Score: $0.35$
  - Payee Novelty: $0.15$
  - Velocity / Urgency: $0.15$
- **Temporal Cross-Signal Boost ($C_{\text{temporal}}$)**:
  - If a suspicious communication ($S_{\text{nlp}} \ge 0.65$) occurred within **15 minutes** before an anomalous transaction, a **$+10.0$ point boost** is applied.
- **Tiers**:
  - `LOW`: $0 - 29.9$
  - `MEDIUM`: $30.0 - 59.9$
  - `HIGH`: $60.0 - 79.9$
  - `CRITICAL`: $80.0 - 100.0$

### Layer 5: Caregiver Escalation & Notification Network (Phase 8/9)
- **Escalation Rules**:
  - `HIGH`: Dispatches SMS alert to designated caregivers.
  - `CRITICAL`: Dispatches concurrent SMS and automated voice emergency call. Bypasses quiet hours.
- **Deduplication**: Prevents repeated alert bursts for the same risk event within sliding time windows.
- **Provider Layer**: `MockTwilioClient` for automated testing and local demos; `RealTwilioClient` for live telecom dispatch when credentials are configured.

### Layer 6: Data Persistence & Auditing
- **Technology**: MongoDB Atlas / mongomock.
- **Collections**: `users`, `transactions`, `alerts`, `analyzed_messages`, `risk_events`, `caregivers`, `notifications`, `notification_preferences`, `revoked_tokens`.
