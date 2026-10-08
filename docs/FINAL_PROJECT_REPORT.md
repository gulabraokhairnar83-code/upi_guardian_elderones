# UPI Guardian: An Explainable Multi-Signal Risk Assessment & Caregiver Safety Network for Digital Payment Protection

**Final Project Technical Report & Dissertation**  
**Phase**: Phase 10 (Final Project Release)  
**Status**: Completed & Verified  

---

## 1. Title
**UPI Guardian: An Explainable Multi-Signal Risk Early-Warning & Caregiver Safety Network for Protecting Senior Citizens in Digital UPI Payments**

---

## 2. Abstract
The rapid proliferation of Unified Payments Interface (UPI) transactions across India has dramatically simplified digital commerce but simultaneously exposed vulnerable demographic cohorts—particularly senior citizens—to sophisticated social engineering scams, coercive phone calls, and phishing payment requests. Existing financial fraud defense mechanisms operate largely post-transaction, relying on retroactive chargebacks and law enforcement reporting after funds have been irreversibly transferred. 

This paper presents **UPI Guardian**, a proactive, explainable risk assessment and caregiver safety platform. The system operates on an event-driven multi-signal architecture combining unsupervised transaction anomaly detection (Isolation Forest), natural language processing for scam communication classification (TF-IDF + Logistic Regression), and an explainable Risk Fusion Engine incorporating temporal cross-signal correlation. When evaluated risk levels reach elevated thresholds (`HIGH` or `CRITICAL`), the platform automatically triggers an emergency escalation pipeline, dispatching multi-channel alerts (SMS and automated voice calls via Twilio) to designated family caregivers with emergency acknowledgement workflows. An intuitive React-based user interface featuring a dedicated "Senior Mode" (scaled typography, minimum 48px touch targets, plain-language advisories) ensures elder accessibility without cognitive overload. Rigorous automated verification across 160 unit/integration tests, zero TypeScript errors, and zero secret leaks confirms the operational readiness and robustness of the proposed framework.

---

## 3. Introduction
Unified Payments Interface (UPI) represents one of the largest real-time retail payment networks globally, processing billions of transactions monthly. Its defining characteristic—instantaneous, non-repudiable account-to-account settlement—makes it an attractive target for digital fraudsters. While younger digital natives frequently identify suspicious links or unsolicited payment requests, elderly individuals often struggle with cognitive fatigue, unfamiliarity with rapid technological shifts, and high susceptibility to fear-based authority threats (e.g., fake electricity bill disconnection, fake police summons, or pension account freezes).

UPI Guardian addresses this critical societal challenge by functioning as an intelligent client/middleware advisory safety net that monitors payment parameters and communication signals submitted to the platform, synthesizes risk signals, and bridges the gap between elderly citizens and their remote caregivers.

---

## 4. Problem Statement
1. **Irreversibility of Real-Time UPI Transfers**: Once a senior citizen enters their 4-digit or 6-digit UPI PIN, the funds are instantly debited and settled; recovery rates through traditional banking complaint mechanisms are low.
2. **Dual-Vector Scam Orchestration**: Modern cyber fraud combines social engineering (intimidating SMS/phone calls) with immediate payment requests. Evaluating financial transactions in isolation from recent communication history creates severe analytical blind spots.
3. **Inaccessible Interfaces for Seniors**: Banking applications are cluttered with complex menus, tiny touch targets, and technical error codes that confuse elderly users during critical moments of coercion.
4. **Lack of Proactive Caregiver Involvement**: Family members usually learn of financial victimization hours or days after the incident has concluded.

---

## 5. Existing System Analysis
| System Type | Mechanism | Key Limitations |
| :--- | :--- | :--- |
| **Traditional Bank Rule Engines** | Static thresholds (e.g., amount $> ₹50,000$) | Rigid; high false positive rate; lacks contextual awareness of incoming scam calls. |
| **Supervised Fraud Models** | Big-data classifiers trained on historical chargebacks | Requires massive labeled fraud data; severe class imbalance ($< 0.01\%$ fraud); privacy concerns. |
| **Caller ID Apps (e.g. Truecaller)** | Community crowd-sourced spam phone numbers | Evaluates phone calls only; completely disconnected from the user's financial payment events. |
| **National Cybercrime Reporting** | Post-incident portal (1930 helpline) | Entirely reactive; operates after the financial loss has already occurred. |

---

## 6. Proposed System Overview
UPI Guardian introduces a multi-tier defense framework:
1. **Unsupervised Transaction Anomaly Detection**: Learns individualized spending patterns using Isolation Forests to detect behavioral deviations without labeled fraud data.
2. **NLP Scam Communication Analysis**: Inspects SMS text and phone transcripts using TF-IDF and Logistic Regression with explainable keyword triggers.
3. **Explainable Risk Fusion Engine**: Integrates transaction anomalies, scam probabilities, payee novelty, and velocity, applying a temporal boost (+10 points) when transactions closely follow scam communications ($\Delta t \le 15\text{ mins}$).
4. **Caregiver Escalation Network**: Automatically notifies nominated family members via SMS and Voice calls during High and Critical risk events with acknowledgement tracking.
5. **Senior Mode User Experience**: Accessible interface tailored for elderly users according to WCAG 2.1 AA principles.

---

## 7. Project Objectives
- Build an explainable multi-signal AI risk assessment system that calculates continuous risk scores ($0.0-100.0$) and categorizes them into discrete tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- Implement an automated caregiver escalation pipeline with multi-channel dispatch (SMS and Voice) and duplicate suppression.
- Provide accessible, senior-friendly interfaces that translate complex machine learning parameters into clear, actionable human advisories.
- Deliver a production-hardened, containerized, and secure software architecture verified by comprehensive regression testing.

---

## 8. Scope of the System
- **In-Scope**:
  - Processing transaction data and communication text supplied to the platform.
  - Multi-signal ML and NLP inference.
  - Caregiver lifecycle management, verification, and preferences.
  - Multi-channel notification dispatch and acknowledgement.
  - Web-based responsive dashboard with Senior Mode.
- **Explicitly Out-of-Scope**:
  - Direct connection to private NPCI banking switches or core banking servers (no bank API access).
  - Storing or processing UPI PINs, net banking passwords, or OTPs.
  - Making definitive, legally binding determinations of confirmed fraud (provides probabilistic early warnings only).

---

## 9. Functional Requirements
- **FR1**: The system must accept transaction payloads (amount, payee, VPA, timestamp, velocity) and return an anomaly risk score.
- **FR2**: The system must accept communication text (SMS/call transcript) and return a scam probability score with trigger keywords.
- **FR3**: The Risk Fusion Engine must synthesize multi-signal scores and apply a temporal boost when cross-signal timing is $\le 15$ minutes.
- **FR4**: Users must be able to authenticate securely using short-lived JWT access tokens and long-lived refresh tokens.
- **FR5**: Elder users must be able to add, verify, update, and manage designated family caregivers.
- **FR6**: The system must dispatch notifications (SMS/Voice) during High and Critical risk events while respecting quiet hours and rate limits.
- **FR7**: Caregivers must be able to view and acknowledge emergency risk alerts.
- **FR8**: The user interface must support toggling between Standard and Senior Mode.

---

## 10. Non-Functional Requirements
- **NFR1 — Latency**: Combined multi-signal model inference must execute in under 15 milliseconds on CPU.
- **NFR2 — Security**: Zero credentials in source code; salted PBKDF2/scrypt password hashing; HTTP security headers (`CSP`, `nosniff`, `X-Frame-Options`); in-memory rate limiting.
- **NFR3 — Reliability**: External telecom failures (e.g. Twilio downtime) must be handled gracefully without crashing transaction analysis.
- **NFR4 — Accessibility**: Compliance with WCAG 2.1 AA targets, visible 3px focus rings, and $\ge 48\text{px}$ touch targets in Senior Mode.
- **NFR5 — Portability**: Hardened Docker containerization for both backend and frontend services.

---

## 11. System Architecture
*(Refer to [`docs/ARCHITECTURE.md`](file:///c:/Users/Dell/Documents/UPI%20Guardian/docs/ARCHITECTURE.md) for full diagram).*

The system operates across six coordinated tiers:
1. **Client Tier**: React 19 / TanStack Start frontend with responsive layouts and Senior Mode.
2. **API Tier**: Flask 3.0 REST service organized via Blueprints with rate limiting and security headers.
3. **ML/NLP Tier**: Pre-trained Isolation Forest and TF-IDF Logistic Regression pipeline models.
4. **Decision Tier**: Risk Fusion Engine with temporal cross-signal correlation logic.
5. **Notification Tier**: Escalation Service with deduplication and Twilio dispatch client.
6. **Data Tier**: MongoDB Atlas database with TTL indexing for token revocation.

---

## 12. Module Description
- **`app.ml`**: Feature engineering, Isolation Forest model loading, inference routines, and decision function score scaling.
- **`app.nlp`**: Text preprocessing, TF-IDF vectorization, Logistic Regression classification, and keyword extraction.
- **`app.risk_fusion`**: Weighted multi-signal fusion, temporal correlation window calculation, and explanation generation.
- **`app.notifications`**: Caregiver resolution, preference evaluation, Twilio client wrapper, and acknowledgement handling.
- **`app.utils`**: Authentication helpers, JWT encoder/decoder, rate limiter, and security headers hook.

---

## 13. Technology Stack
- **Frontend**: React 19, TypeScript, TanStack Start, TanStack Router, Vite 8, Tailwind CSS v4, Lucide React, Recharts.
- **Backend**: Python 3.11, Flask 3.0, Werkzeug 3.0, PyJWT 2.8, Gunicorn 21.2.
- **Data Science**: Scikit-learn 1.4, Pandas 2.2, NumPy 1.26, Joblib 1.3.
- **Database**: MongoDB Atlas / PyMongo 4.6 (with `mongomock` development fallback).
- **Telecom**: Twilio Python SDK 9.0 (with mock client simulator).
- **DevOps**: Docker, Docker Compose.

---

## 14. Database Design
MongoDB document-oriented architecture across 9 verified collections:
- `users`: Identity, role, salted password hashes.
- `transactions`: Historical payments, amounts, payee VPAs, anomaly scores.
- `alerts`: Active and resolved in-app notifications.
- `analyzed_messages`: Scanned communication logs, scam probabilities, keyword tags.
- `risk_events`: Fused multi-signal evaluations with temporal correlation flags.
- `caregivers`: Caregiver relationships, contact details, verification flags.
- `notifications`: Dispatch logs, provider SIDs, channel, status, acknowledgement.
- `notification_preferences`: Quiet hours and channel configurations.
- `revoked_tokens`: Blacklisted JWT identifiers with native MongoDB TTL index auto-cleanup.

---

## 15. Machine Learning Methodology (Transaction Anomaly)
- **Algorithm**: Isolation Forest.
- **Training Strategy**: Trained on synthetic baseline transaction distributions representing habitual elder spending (groceries, utilities, medicines) interspersed with anomalous spikes.
- **Feature Space**: Transaction Amount (log-normalized), Payee Novelty (binary), Velocity (transfers in 24h), Time-of-Day deviation, Transaction Type (P2P, P2M).
- **Inference**: Produces decision function score normalized to $[0.0, 1.0]$. Latency: $< 5\text{ms}$.

---

## 16. NLP Methodology (Scam Communication Analysis)
- **Algorithm**: TF-IDF Vectorizer + Logistic Regression.
- **Text Processing**: Lowercase conversion, punctuation stripping, phone/URL tokenization.
- **N-Gram Range**: Unigrams and bigrams $(1, 2)$ with sublinear term frequency.
- **Calibration**: Probability calibrated using sigmoid activation. Extracts top positive feature coefficients as human-interpretable scam indicators. Latency: $< 8\text{ms}$.

---

## 17. Risk Fusion Methodology
- **Composite Equation**:
  $$\text{Fused Score} = (0.35 \cdot S_{\text{anomaly}}) + (0.35 \cdot S_{\text{nlp}}) + (0.15 \cdot S_{\text{payee}}) + (0.15 \cdot S_{\text{velocity}}) + C_{\text{temporal}}$$
- **Temporal Boost**: If $\Delta t(\text{transaction}, \text{scam}) \le 15\text{ minutes}$, add $+10.0$ points.
- **Tiers**:
  - `LOW` ($0.0 - 29.9$): Normal.
  - `MEDIUM` ($30.0 - 59.9$): Caution.
  - `HIGH` ($60.0 - 79.9$): Warning (Caregiver SMS).
  - `CRITICAL` ($80.0 - 100.0$): Urgent (Caregiver SMS + Voice Call).

---

## 18. Authentication & Session Management
- Stateless JSON Web Tokens (HS256).
- Short-lived access tokens (15–60 minutes) paired with 7-day refresh tokens.
- Server-side token revocation on logout via indexed TTL blacklist.
- Protection against account deactivation and user enumeration.

---

## 19. Caregiver Notification System
- Multi-channel notification pipeline (SMS and Voice calls via Twilio).
- Safe development baseline (`TWILIO_ENABLED=false`) backed by `MockTwilioClient`.
- Automated deduplication preventing alert fatigue.
- Quiet-hours policy (10:00 PM – 7:00 AM) bypassed strictly during `CRITICAL` risk events.
- Caregiver emergency acknowledgement with recorded audit timestamps.

---

## 20. Security Hardening
- **Zero Secrets in Code**: Sourced exclusively through environment variables.
- **Rate Limiting**: Sliding-window in-memory limiter on auth and escalation endpoints.
- **Security Headers**: Standard OWASP headers attached to every HTTP response.
- **Error Sanitation**: Generic 500 error responses with zero traceback or database string leakage.

---

## 21. Accessibility Evaluation
- Internal WCAG 2.1 AA evaluation verified.
- Dedicated Senior Mode providing 112% text scaling and $\ge 48\text{px}$ touch targets.
- Universal `Escape` key dismissal for modals and drawers.
- High-contrast OKLCH color palettes across light and dark modes.

---

## 22. Testing & Quality Assurance
- **Unit & Integration Suite**: 160 automated backend tests (`pytest -q`) passing with 100% pass rate.
- **Frontend Verification**: `npx tsc --noEmit` exited with 0 errors; `npm run build` compiled cleanly.
- **Manual End-to-End**: 17-step mock E2E script executed successfully across the entire user lifecycle.
- **Secret Scan**: Automated repository-wide regex scan confirmed 0 leaked credentials.

---

## 23. Results & Evaluation Summary
The system demonstrated flawless cross-signal risk escalation:
- In Scenario 1 (Low Risk), payments executed seamlessly with green safety badges.
- In Scenario 4 (Critical Risk), a ₹75,000 late-night transfer following an urgent scam call triggered a 100/100 risk score, an immediate SMS alert, and an automated voice call to the designated caregiver, with immediate acknowledgement capabilities and zero duplicate alerts.

---

## 24. Limitations
1. **In-Memory Rate Limiting**: The sliding-window rate limiter runs in-process. For horizontally scaled cloud clusters, an external Redis cache is recommended.
2. **Synthetic Data Calibration**: Models were trained on synthetic distributions; real-world deployment requires continuous tuning with real payment telemetry.
3. **Twilio Webhook Live Signature Validation**: Production live signature verification requires registering a public HTTPS domain with the Twilio Console.

---

## 25. Future Scope
- Integration with regional Indian language NLP models (Hindi, Marathi, Tamil, Bengali) to detect localized scam communications.
- Integration with on-device Android accessibility services for real-time overlay alerts during UPI application usage.
- Distributed Redis caching for horizontally clustered production rate limiting.

---

## 26. Conclusion
UPI Guardian demonstrates that explainable artificial intelligence, when paired with thoughtful accessible design and automated caregiver safety escalation, can provide an effective, non-intrusive early-warning shield for senior citizens navigating the digital payment ecosystem. By focusing on explainability, privacy minimization, and human-in-the-loop verification, the platform empowers elderly citizens to transact with dignity and peace of mind.

---

## 27. References
1. National Payments Corporation of India (NPCI), "UPI Product Statistics & Growth Reports", 2024–2026.
2. Liu, F. T., Ting, K. M., & Zhou, Z. H., "Isolation Forest", *IEEE International Conference on Data Mining (ICDM)*, 2008.
3. World Wide Web Consortium (W3C), "Web Content Accessibility Guidelines (WCAG) 2.1", W3C Recommendation, 2018.
4. Reserve Bank of India (RBI), "Master Direction on Digital Payment Security Controls", Reserve Bank of India, 2021.
5. Pedregosa et al., "Scikit-learn: Machine Learning in Python", *Journal of Machine Learning Research*, 2011.
