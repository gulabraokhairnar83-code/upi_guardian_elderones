# UPI Guardian

> **An Explainable Multi-Signal Risk Assessment & Caregiver Safety Network for Digital UPI Payments**

---

## 1. Project Title
**UPI Guardian: AI-Assisted Early-Warning & Caregiver Safety System for UPI Financial Protection**

---

## 2. Project Overview
UPI Guardian is a proactive, explainable financial safety and risk early-warning platform designed specifically to protect senior citizens from payment fraud and predatory scam communications (SMS and voice calls). By integrating transaction behavioral anomaly detection with natural language communication analysis and an automated caregiver escalation pipeline, UPI Guardian introduces human-in-the-loop protection before irreversible funds transfers occur.

---

## 3. Problem Statement
The Unified Payments Interface (UPI) provides instant, non-repudiable financial settlement. While convenient, this real-time finality makes senior citizens prime targets for social engineering, coercive phone calls, and phishing messages. Elderly users often suffer from digital unfamiliarity and cognitive fatigue, making them susceptible to artificial urgency (e.g., fake bill disconnections, fake police summons, or pension locks). Traditional security operates post-incident, leaving victims with unrecoverable losses.

---

## 4. Proposed Solution
UPI Guardian provides an intelligent early-warning layer that:
- Detects unusual deviations in transaction behavior using unsupervised machine learning.
- Analyzes incoming messages and call transcripts for known scam patterns and social engineering tactics.
- Synthesizes transaction and communication signals using an explainable Risk Fusion Engine.
- Escalates high-risk events to trusted family caregivers via multi-channel alerts (SMS and automated voice calls).
- Delivers a dedicated "Senior Mode" interface featuring high contrast, enlarged fonts, and clear, non-technical advisories.

---

## 5. Key Features
- **Senior-Centric UI**: Dynamic Senior Mode toggle providing 112% base text scaling and $\ge 48\text{px}$ touch targets.
- **Behavioral Anomaly Engine**: Scans amount, velocity, payee novelty, and temporal features using Isolation Forest.
- **NLP Scam Classifier**: Scans text messages and call transcripts for scam indicators using TF-IDF + Logistic Regression.
- **Explainable Risk Fusion**: Combines signals into an interpretable score ($0-100$) and four risk tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Temporal Cross-Signal Boost**: Adds a $+10$ point boost when a payment closely follows an urgent scam message ($\Delta t \le 15\text{ mins}$).
- **Automated Caregiver Escalation**: Dispatches SMS and voice calls via Twilio during Critical and High risk events.
- **Idempotency & Deduplication**: Prevents alert fatigue by dropping duplicate notifications for the same risk event.
- **Caregiver Emergency Acknowledgement**: Enables remote caregivers to review alerts and mark situations safe in real time.

---

## 6. System Architecture
```
User / Elder
      │
      ▼
React 19 Frontend (Senior Mode / High Contrast UI)
      │
      │  JWT Bearer (HS256)
      ▼
Flask REST API Engine
      │
      ├─────────────────────────────┐
      ▼                             ▼
Authentication Service         Application APIs
      │                             │
      ▼                             ▼
MongoDB Atlas ◄────────────── Risk Fusion Engine
                                    │
                      ┌─────────────┴─────────────┐
                      ▼                           ▼
            Isolation Forest               NLP Classifier
           (Anomaly Detector)             (Scam Analyzer)
                      │                           │
                      └─────────────┬─────────────┘
                                    │
                                    ▼
                             Fused Risk Score
                              (0.0 to 100.0)
                                    │
                      ┌─────────────┴─────────────┐
                      ▼                           ▼
                 LOW / MEDIUM                HIGH / CRITICAL
                                                  │
                                                  ▼
                                         Caregiver Escalation
                                                  │
                                                  ▼
                                            Twilio Dispatch
                                         (SMS / Voice Alerts)
```

---

## 7. Technology Stack
- **Frontend**: React 19, TypeScript, TanStack Start, TanStack Router, Vite 8, Tailwind CSS v4, Lucide Icons, Recharts.
- **Backend**: Python 3.11, Flask 3.0, Werkzeug 3.0, PyJWT 2.8, Gunicorn 21.2.
- **Machine Learning**: Scikit-learn 1.4, Pandas 2.2, NumPy 1.26, Joblib 1.3.
- **Database**: MongoDB Atlas / PyMongo 4.6 (with `mongomock` in-memory fallback).
- **Telecom**: Twilio Python SDK 9.0 (with mock client simulator).
- **DevOps**: Docker, Docker Compose.

---

## 8. Machine Learning Architecture
- **Model**: Scikit-learn **Isolation Forest** (`n_estimators=100`, `contamination=0.08`).
- **Features**: Normalized transaction amount, payee novelty indicator, 24-hour transaction frequency (velocity), time-of-day deviation, and payment type.
- **Inference**: Produces decision function score normalized to $[0.0, 1.0]$. Average execution latency $< 5\text{ms}$. Pre-packaged in `backend/app/ml/models/artifacts/transaction_anomaly_detector.joblib`.

---

## 9. NLP Architecture
- **Model**: **TF-IDF Vectorizer** (unigram + bigram, sublinear TF) paired with **Logistic Regression** (`C=1.5`).
- **Features**: Extracted scam phrase indicators (e.g., `account_locked`, `urgent_kyc`, `electricity_disconnected`, `safety_account`).
- **Inference**: Returns calibrated scam probability $[0.0, 1.0]$ with top explanatory keyword triggers. Average latency $< 8\text{ms}$. Pre-packaged in `backend/app/nlp/models/artifacts/scam_classifier.joblib`.

---

## 10. Risk Fusion Architecture
- **Composite Formula**:
  $$\text{Fused Score} = (0.35 \cdot S_{\text{anomaly}}) + (0.35 \cdot S_{\text{nlp}}) + (0.15 \cdot S_{\text{payee}}) + (0.15 \cdot S_{\text{velocity}}) + C_{\text{temporal}}$$
- **Temporal Correlation ($C_{\text{temporal}}$)**: Applies $+10.0$ point boost if $\Delta t(\text{transaction}, \text{scam}) \le 15\text{ minutes}$.
- **Tiers**: `LOW` ($0.0-29.9$), `MEDIUM` ($30.0-59.9$), `HIGH` ($60.0-79.9$), `CRITICAL` ($80.0-100.0$).

---

## 11. Authentication Architecture
- Stateless JSON Web Tokens (JWT) adhering to RFC 7519 using `HS256`.
- Short-lived access tokens (15–60 mins) and long-lived refresh tokens (7 days).
- Token revocation blacklist stored in MongoDB with native TTL index auto-cleanup (`expireAfterSeconds=0`).
- Account deactivation checks prevent inactive users from authenticating.
- Salted PBKDF2/scrypt password hashing with zero password or hash exposure across API responses.

---

## 12. Caregiver Notification Architecture
- Automatic dispatch of SMS and automated voice calls during `HIGH` and `CRITICAL` events.
- Default safe development mode (`TWILIO_ENABLED=false`) backed by `MockTwilioClient`.
- Notification deduplication prevents repeated alerts for identical events.
- Hourly caregiver rate limit (max 3 alerts/hour).
- Quiet hours (10:00 PM – 7:00 AM) bypassed strictly during `CRITICAL` risk events.

---

## 13. Database Design
MongoDB document-oriented architecture across 9 collections:
- `users`: User accounts and hashed credentials.
- `transactions`: Evaluated payment logs and anomaly scores.
- `alerts`: Active and resolved in-app notifications.
- `analyzed_messages`: Inbound communication analysis records.
- `risk_events`: Immutable audit trail of fused risk assessments.
- `caregivers`: Caregiver relationships, contact details, verification status.
- `notifications`: History of SMS/Voice dispatches and emergency acknowledgements.
- `notification_preferences`: Quiet hours and notification channels.
- `revoked_tokens`: Blacklisted JWT identifiers with native TTL auto-cleanup.

---

## 14. API Overview
- `POST /api/auth/register`: User account creation with role assignment.
- `POST /api/auth/login`: Authentication with JWT token pair generation.
- `POST /api/auth/refresh`: Token refresh using valid refresh token.
- `POST /api/auth/logout`: Server-side token revocation.
- `GET /api/auth/me`: Profile retrieval.
- `POST /api/analyze-transaction`: Transaction anomaly detection.
- `POST /api/analyze-message`: NLP scam communication analysis.
- `POST /api/risk/analyze`: Multi-signal Risk Fusion evaluation.
- `GET /api/caregivers`: Caregiver directory management.
- `POST /api/notifications/<id>/acknowledge`: Emergency alert acknowledgement.
- `POST /api/notifications/webhook`: Provider delivery status receipt callback.
- `GET /api/health`: Service health probe.

---

## 15. Project Structure
```
UPI-GUARDIAN/
├── backend/
│   ├── app/
│   │   ├── db/                 # Database connection & repositories
│   │   ├── ml/                 # Isolation Forest anomaly engine
│   │   ├── nlp/                # TF-IDF scam classifier
│   │   ├── notifications/      # Twilio escalation & deduplication
│   │   ├── risk_fusion/        # Cross-signal Risk Fusion Engine
│   │   ├── routes/             # REST API Blueprints
│   │   ├── schemas/            # Request validators & boundary guards
│   │   └── utils/              # JWT, rate limiter, security headers
│   ├── tests/                  # 160 unit, integration & security tests
│   ├── Dockerfile              # Multi-stage production Python container
│   ├── requirements.txt        # Backend dependencies
│   └── .env.example            # Environment configuration template
│
├── frontend-magic-wand-07-main/
│   ├── src/                    # React 19 / TanStack Start source code
│   ├── public/                 # Static assets
│   ├── Dockerfile              # Multi-stage production Node container
│   ├── package.json            # Frontend dependencies
│   └── .env.example            # Frontend environment template
│
├── docs/                       # Technical reports & specifications
├── docker-compose.yml          # Local container orchestration
├── README.md                   # Project documentation
└── .gitignore                  # Git secret and artifact exclusion rules
```

---

## 16. Local Setup

### Backend (Python 3.11+)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run full automated test suite (160 tests)
pytest -q

# Run manual end-to-end flow with mock Twilio
python tests/run_phase8_manual_e2e.py

# Launch development server
python run.py
```

### Frontend (Node 20+)
```bash
cd frontend-magic-wand-07-main
npm install

# TypeScript verification (0 errors)
npx tsc --noEmit

# Production build verification
npm run build

# Launch development server
npm run dev
```

---

## 17. Environment Variables
- **Backend (`backend/.env`)**:
  - `FLASK_ENV`: `development` or `production`
  - `SECRET_KEY`: High-entropy session key
  - `JWT_SECRET_KEY`: High-entropy JWT signing key
  - `MONGODB_URI`: MongoDB Atlas connection URI (leave blank for local `mongomock`)
  - `TWILIO_ENABLED`: Set `false` for offline mock mode; `true` for live telecom dispatch
- **Frontend (`frontend-magic-wand-07-main/.env`)**:
  - `VITE_API_BASE_URL`: URL to backend Flask service (`http://127.0.0.1:5000/api`)
  - `VITE_USE_MOCK_API`: Set `false` for live backend; `true` for standalone offline demo

---

## 18. Docker Setup
Launch both services locally in isolated containers:
```bash
# Build and run container stack
docker compose up -d --build

# Verify container health probes
docker compose ps

# View logs
docker compose logs -f
```

---

## 19. Testing
- **Backend Regression Suite**: **160 / 160 Passed** (`pytest -q` in 5.38s).
- **Frontend Typecheck**: **0 Errors** (`npx tsc --noEmit`).
- **Production Build**: **Compiled Cleanly** (`npm run build`).
- **Manual E2E Flow**: **17 / 17 Steps Verified** (`tests/run_phase8_manual_e2e.py`).
- **Secret Scan**: **0 Leaked Credentials Detected**.

---

## 20. Deployment Strategy
- **Backend Container**: Deploy to managed container platforms (Render, AWS ECS, or Google Cloud Run) using `backend/Dockerfile` with Gunicorn WSGI.
- **Frontend Client**: Deploy static output (`.output/public`) to edge CDNs (Vercel, Cloudflare Pages, or Render Static Sites).
- **Database**: Dedicated MongoDB Atlas cluster with restricted IP allowlists.

---

## 21. Security Posture
- **Zero Hardcoded Secrets**: All keys managed via environment variables.
- **Rate Limiting**: Sliding-window rate limiter prevents brute-force authentication.
- **OWASP Security Headers**: Enforces `nosniff`, `DENY` frames, `CSP`, and conditional `HSTS`.
- **Error Sanitation**: Unhandled exceptions return generic 500 JSON without stack traces.

---

## 22. Accessibility Compliance
- Internal audit targets **WCAG 2.1 Level AA** standards.
- Senior Mode provides 112% base text scaling and $\ge 48\text{px}$ touch targets.
- Keyboard accessible with universal `Escape` key dismissal for modals and drawers.
- High-contrast OKLCH color palettes across light and dark modes.

---

## 23. Limitations
1. **In-Memory Rate Limiter**: Single-process rate limiting; horizontally clustered cloud deployments require an external Redis cache.
2. **Synthetic Data Baseline**: Models trained on synthetic distributions; production calibration with live banking telemetry is recommended.
3. **Twilio Webhook Verification**: Live HMAC signature validation requires public HTTPS domain registration in the Twilio Console.

---

## 24. Future Scope
- Integration with regional Indian language NLP models (Hindi, Marathi, Tamil, Bengali).
- Real-time Android accessibility overlay during third-party UPI application execution.
- Distributed Redis caching for horizontally clustered production rate limiting.

---

## 25. Disclaimer
UPI Guardian is an **AI-assisted early-warning risk advisory system**. It does **not** directly interface with private NPCI core banking switches or freeze bank accounts. It evaluates transaction and communication data submitted to the platform to generate early risk warnings and facilitate caregiver verification. It does **not** make legally binding determinations of confirmed fraud.
