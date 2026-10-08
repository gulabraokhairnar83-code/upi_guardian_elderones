# UPI Guardian — Technical Viva & Defense Guide (30 Questions & Answers)

**Audience**: Project Evaluators, University Examination Boards, Defense Committees  
**Project**: UPI Guardian (Explainable AI Early-Warning & Caregiver Safety Network)  

---

### Q1: Why did you choose this project?
**Answer**: Digital payments via UPI have grown exponentially in India, transforming financial inclusion. However, cybercriminals increasingly target senior citizens through social engineering, fake KYC SMS, and coercive phone scams. Most existing security solutions are post-facto (relying on police reports or bank chargebacks days later). We chose to build a proactive, real-time, explainable early-warning system that empowers senior citizens and their trusted family caregivers before funds leave the account.

---

### Q2: What exact problem does UPI Guardian solve?
**Answer**: It bridges the cognitive and technical gap senior citizens face when interacting with UPI. Seniors often struggle to distinguish between legitimate bank notifications and phishing scams, especially when subjected to artificial urgency. UPI Guardian analyzes both financial payment anomalies and suspicious incoming communications, fuses them, and alerts family caregivers immediately when high-risk patterns emerge.

---

### Q3: Why specifically target elderly users?
**Answer**: Seniors are disproportionately vulnerable to social engineering due to digital unfamiliarity, fear of authority (e.g., fake police/tax threats), and natural cognitive decline. Furthermore, standard banking apps feature cluttered interfaces and small fonts. UPI Guardian provides a specialized "Senior Mode" with 112% scaled typography, 48px touch targets, and plain-language guidance ("Please stop and verify this payment") rather than technical error codes.

---

### Q4: Why did you use Isolation Forest for transaction anomaly detection?
**Answer**: Isolation Forest is an unsupervised tree-based algorithm uniquely suited for anomaly detection. Unlike traditional clustering algorithms that calculate expensive pairwise distances, Isolation Forest isolates anomalies by randomly selecting a feature and split value. Because anomalies are "few and different," they require fewer random recursive splits to be isolated, resulting in much shorter path lengths in the isolation trees. This provides sub-5ms inference latency and high sensitivity without requiring labeled fraud datasets.

---

### Q5: Why not use Random Forest instead of Isolation Forest?
**Answer**: Random Forest is a **supervised** classification algorithm requiring massive, well-balanced labeled datasets of both "legitimate" and "confirmed fraud" transactions. In real-world UPI payment environments, confirmed fraud represents less than 0.01% of all traffic (extreme class imbalance), and obtaining labeled fraud data violates banking privacy. Isolation Forest operates **unsupervised**, learning the boundary of normal individual behavior and isolating outliers without needing prior fraud labels.

---

### Q6: Why did you use synthetic data for training?
**Answer**: Real UPI financial transactions contain sensitive personal identifiable information (PII), bank account numbers, phone numbers, and payment habits protected by banking privacy laws (e.g., RBI guidelines and the DPDP Act). Using synthetic data allowed us to model authentic behavioral distributions (merchant frequencies, diurnal cycles, velocity spikes, and scam scripts) in a privacy-compliant, reproducible, and legally safe manner.

---

### Q7: What is anomaly detection from a data science perspective?
**Answer**: Anomaly detection is the identification of rare observations, items, or events that raise suspicions by differing significantly from the majority of the data. In our platform, an anomaly does not mean "confirmed crime"; it means a transaction deviates statistically from the established baseline pattern of that specific user.

---

### Q8: What constitutes "behavioral deviation" in your model?
**Answer**: Behavioral deviation measures divergence across multiple orthogonal user features:
1. Transaction amount relative to historical median and standard deviation.
2. Novelty of the payee VPA (whether the user has ever transacted with this merchant before).
3. Payment time of day (e.g., payments made at 2:00 AM vs 10:00 AM).
4. Velocity (number of transactions attempted in the preceding 60-minute and 24-hour windows).

---

### Q9: What is "velocity" and why does it matter?
**Answer**: Velocity is the rate of transactions or payments over a rolling time window. When scammers take control of an elderly victim's trust, they often induce rapid, consecutive payment attempts (e.g., 3 transfers within 15 minutes) before the victim can consult family. A sudden spike in velocity is one of the strongest statistical indicators of coercive fraud.

---

### Q10: Why did you choose TF-IDF for communication text representation?
**Answer**: Term Frequency-Inverse Document Frequency (TF-IDF) effectively highlights words that are distinctively frequent in scam messages (e.g., "KYC", "blocked", "lottery", "electricity bill", "disconnected", "penalty") while down-weighting ubiquitous grammatical words ("the", "is", "your"). By utilizing both unigrams and bigrams with sublinear term frequency scaling, the vectorizer captures phrase-level context with minimal compute and memory overhead.

---

### Q11: Why pair TF-IDF with Logistic Regression instead of Deep Learning (e.g., BERT/LLMs)?
**Answer**: 
1. **Inference Latency**: Logistic Regression computes text classification in $< 8\text{ms}$ on CPU, compared to 200–800ms for heavy Transformer models.
2. **Explainability**: Logistic Regression coefficients directly map to feature weights. We can extract the top positive weights to immediately tell the user which exact words triggered the scam classification (e.g., `"account_locked"`: $+2.8$).
3. **Deployment Footprint**: The entire TF-IDF + Logistic Regression pipeline compiles to a compact $\sim 3\text{MB}$ artifact, avoiding multi-gigabyte GPU container dependencies.

---

### Q12: How does the NLP scam classifier work?
**Answer**: Inbound text (SMS or digitized call transcript) is preprocessed (lowercasing, symbol cleanup, URL masking). The text is transformed into a sparse TF-IDF feature vector. The Logistic Regression model applies a calibrated sigmoid function to calculate a probability score between $0.0$ and $1.0$. If the score exceeds $0.65$, it is flagged as a potential scam communication.

---

### Q13: What is the "Risk Fusion Engine"?
**Answer**: The Risk Fusion Engine is the centralized decision core of UPI Guardian. Individual models (anomaly detection, text classification) provide isolated signals. The fusion engine synthesizes these disparate signals into a unified, mathematically bounded risk score between $0$ and $100$ and categorizes it into four discrete actionable tiers: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.

---

### Q14: Why is combining transaction and communication signals superior to evaluating them separately?
**Answer**: Social engineering scams rarely happen in isolation; an intimidating phone call or phishing SMS almost always precedes the fraudulent transfer. A ₹40,000 transaction by itself might look like an uncommon but legitimate home appliance purchase. A scam SMS by itself might just be deleted. But when a ₹40,000 payment to an unknown payee occurs **immediately after** an urgent scam SMS, the combined probability of fraud approaches certainty. Evaluating them together eliminates blind spots.

---

### Q15: What is "Temporal Cross-Signal Correlation"?
**Answer**: Temporal correlation is our cross-signal mechanism that evaluates the time difference ($\Delta t$) between an anomalous transaction and a detected scam communication. If $\Delta t \le 15\text{ minutes}$ and both signals are elevated, the system applies an automated **$+10.0$ point temporal boost** to the final risk score.

---

### Q16: How is the final risk score calculated?
**Answer**:
$$\text{Score} = (0.35 \cdot S_{\text{anomaly}}) + (0.35 \cdot S_{\text{nlp}}) + (0.15 \cdot S_{\text{payee}}) + (0.15 \cdot S_{\text{velocity}}) + C_{\text{temporal}}$$
Where $S_{\text{anomaly}}$ is normalized Isolation Forest score ($0-100$), $S_{\text{nlp}}$ is scam text probability ($0-100$), $S_{\text{payee}}$ is payee novelty ($0$ or $100$), $S_{\text{velocity}}$ is frequency score ($0-100$), and $C_{\text{temporal}}$ is the $+10$ correlation boost (applied when $\Delta t \le 15\text{ mins}$). The final value is capped at $100.0$.

---

### Q17: What do the risk tiers (LOW, MEDIUM, HIGH, CRITICAL) mean?
**Answer**:
- **LOW ($0-29.9$)**: Normal transaction; green badge; standard execution.
- **MEDIUM ($30.0-59.9$)**: Elevated caution; yellow badge; advisory message to verify merchant.
- **HIGH ($60.0-79.9$)**: High risk; orange warning; automated SMS dispatch to family caregiver.
- **CRITICAL ($80.0-100.0$)**: Severe threat; red overlay; immediate concurrent SMS + automated voice call to caregiver, bypassing quiet hours.

---

### Q18: How does the Caregiver Escalation Service work?
**Answer**: When a risk event reaches `HIGH` or `CRITICAL`, the escalation service identifies the elder's active, verified caregivers. It inspects caregiver notification preferences (SMS/Voice enabled), evaluates quiet hours, checks hourly rate limits (maximum 3 alerts/hour), and dispatches the alert via the Twilio client.

---

### Q19: Why did you use stateless JWT for authentication?
**Answer**: JSON Web Tokens provide secure, self-contained identity claims without requiring server-side session state in memory. We implemented short-lived access tokens (15–60 mins) paired with long-lived refresh tokens (7 days). Token revocation on logout is managed via an indexed MongoDB blacklist with automated TTL expiration.

---

### Q20: Why did you choose MongoDB Atlas?
**Answer**: Fraud audit events, transaction logs, and notification dispatches have variable, semi-structured schemas (e.g., differing metadata between SMS vs Voice alerts). MongoDB's flexible BSON document model allows seamless iteration, while Atlas provides managed cloud scaling, automated replication, SSL encryption, and native TTL collection indexing.

---

### Q21: Why choose Flask over FastAPI or Django?
**Answer**: Flask provides a clean, un-opinionated WSGI micro-framework. It allows us to architect modular Blueprints, implement custom security headers, integrate Scikit-learn models natively, and run lightweight Gunicorn workers without the heavy ORM overhead of Django or the ASGI async typing complexities of FastAPI.

---

### Q22: Why choose React 19 and TanStack Router/Start?
**Answer**: TanStack Router provides 100% type-safe routing, search parameter validation, and fast client-side transitions. React 19 gives us modern component composition, enabling seamless state management for our Senior Mode context, dark/light theme switcher, and real-time risk gauges.

---

### Q23: How is password security handled?
**Answer**: Passwords are never stored in plaintext. They are salted and hashed using Werkzeug's implementation of `scrypt`/`pbkdf2`. Passwords require at least 8 characters with letters and numbers. Password hashes are strictly stripped from all API outputs, and login failures return generic `"Invalid email or password"` responses to prevent email enumeration.

---

### Q24: How are Twilio credentials protected?
**Answer**: Twilio Account SID, Auth Token, and Sender Phone numbers are backend-only environment variables (`TWILIO_ACCOUNT_SID`, etc.). They are never exposed to the frontend bundle or client network responses. Furthermore, `TWILIO_ENABLED=false` is enforced as the default baseline so live telecom calls can never be triggered accidentally without explicit administrative configuration.

---

### Q25: How do you prevent duplicate caregiver notifications?
**Answer**: The system enforces **Idempotency and Deduplication**. Before dispatching, `NotificationRepository.find_duplicate()` checks if a notification with the same `risk_event_id`, `caregiver_id`, and `channel` has already been created in an active state (`SENT`, `DELIVERED`, `PENDING`). If found, subsequent dispatches are dropped immediately.

---

### Q26: What happens if Twilio or an external telecom API fails?
**Answer**: Telecom errors are caught cleanly within try/except blocks inside `RealTwilioClient`. The system records the failure status (`status: "FAILED"`, `error_code: ...`) in the database, but **never crashes** the transaction analysis or returns a 500 server error to the senior citizen.

---

### Q27: What are the current technical limitations of the platform?
**Answer**:
1. **In-Memory Rate Limiting**: The current sliding-window limiter stores request timestamps in Python memory, which is effective for single-instance containers but requires an external Redis cache for horizontally clustered nodes.
2. **Synthetic Data Baseline**: Models were trained on realistic synthetic distributions; production deployment would benefit from continuous real-world calibration.
3. **Twilio Webhook Verification**: Live HMAC signature verification requires public HTTPS domain registration with Twilio.

---

### Q28: What is the primary novelty of this project?
**Answer**: Potential novelty lies in combining behavioral transaction deviation, unsupervised transaction anomaly detection, NLP scam classification, and temporal cross-signal correlation into an explainable, dual-user risk warning workflow tailored specifically for elderly citizens and remote caregivers.

---

### Q29: Does UPI Guardian directly access or freeze bank accounts?
**Answer**: **No.** UPI Guardian does not have direct access to core banking switches or the private NPCI UPI network. It functions as an intelligent client/middleware advisory layer that evaluates transaction and communication parameters submitted to it. It guides the user and notifies caregivers, but does not execute unauthorized bank-level asset freezes.

---

### Q30: Is the system guaranteed to detect 100% of fraud?
**Answer**: **No system can guarantee 100% fraud detection.** Zero false positives and zero false negatives are impossible in probabilistic machine learning. UPI Guardian is explicitly designed and presented as an **early-warning risk advisory system**, not an absolute fraud guarantee. It provides timely alerts to introduce human verification at the critical moment of decision.
