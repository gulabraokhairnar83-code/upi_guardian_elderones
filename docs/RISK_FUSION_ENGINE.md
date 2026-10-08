# UPI Guardian — Risk Fusion Engine & Cross-Signal Correlation

> **Architecture Document — Phase 6**  
> **Status:** Implemented & Verified  
> **Engine Type:** Transparent Multi-Signal Risk Aggregation & Temporal Correlation Layer (Deterministic Business-Logic Layer; Not an opaque secondary ML model)

---

## 1. Purpose & Core Philosophy

**UPI Guardian** is designed to protect vulnerable demographics (especially senior citizens) from sophisticated, multi-stage cyber financial fraud in India. Modern UPI frauds are rarely isolated events; they typically combine:
1. **Psychological coercion** via SMS or phone calls (e.g., electricity disconnection threats, digital arrest impersonation, KYC deactivation warnings), followed by
2. **Induced UPI transactions** to unfamiliar mule accounts or fake merchant handles under extreme urgency.

Prior to Phase 6, UPI Guardian had two isolated detection pillars:
- **Phase 4:** Isolation Forest Machine Learning model for **Transaction Anomaly Detection**.
- **Phase 5:** TF-IDF + Calibrated Logistic Regression model for **Scam Communication Classification**.

The **Risk Fusion Engine (Phase 6)** synthesizes these disparate signals into a unified, explainable composite risk score $[0, 100]$ alongside actionable, elder-friendly guidance.

> [!IMPORTANT]
> **Safety and Scope Boundary:**
> - Isolation Forest detects anomalous transaction behavior.
> - NLP detects suspicious/scam-like communication patterns.
> - Risk Fusion aggregates these signals into a composite early-warning assessment.
> - **The final score is NOT proof of confirmed fraud.** The system never accuses recipients or claims "Fraud confirmed"; it strictly uses advisory phrasing such as *"Potential scam detected"*, *"High-risk activity detected"*, or *"Suspicious activity detected"*.

---

## 2. Multi-Signal Architecture

```
                  ┌────────────────────────────────────────┐
                  │          Incoming Transaction          │
                  │  (Amount, Payee, UPI ID, Timestamp)    │
                  └───────────────────┬────────────────────┘
                                      │
            ┌─────────────────────────┼────────────────────────┐
            ▼                         ▼                        ▼
┌────────────────────────┐┌────────────────────────┐┌────────────────────────┐
│  Phase 4 ML Engine     ││   User History Baseline││ Phase 5 NLP Database   │
│  (Isolation Forest)    ││  (Mean, Std, Payees)   ││ (Recent Scam Analysis) │
└───────────┬────────────┘└───────────┬────────────┘└───────────┬────────────┘
            │                         │                         │
            ▼                         ▼                         ▼
┌────────────────────────┐┌────────────────────────┐┌────────────────────────┐
│ Transaction Anomaly    ││  Behavioral Deviation  ││ Temporal Correlation   │
│      Score (35%)       ││   & Payee Novelty      ││     Engine (120 min)   │
└───────────┬────────────┘└───────────┬────────────┘└───────────┬────────────┘
            │                         │                         │
            └─────────────────────────┼─────────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │    Risk Fusion Engine     │
                        │ - Normalized Signal Sum   │
                        │ - Cross-Signal Boost (+10)│
                        │ - Score Clamping [0, 100] │
                        └─────────────┬─────────────┘
                                      │
            ┌─────────────────────────┴────────────────────────┐
            ▼                                                  ▼
┌───────────────────────────┐                      ┌───────────────────────────┐
│   Explainability Layer    │                      │  Persistence & Alerts     │
│ - Top Contributing Factors│                      │ - risk_events (MongoDB)   │
│ - Elder-Friendly Guidance │                      │ - alerts (Deduplicated)   │
└───────────────────────────┘                      └───────────────────────────┘
```

---

## 3. The 6 Multi-Signals

Every signal is normalized to the standard continuous scale of $[0.0, 100.0]$:

| Signal Name | Source | Description | Weight |
|---|---|---|:---:|
| `transaction_anomaly_score` | Phase 4 Isolation Forest | Divergence of numerical transaction features from the trained distribution. | **35%** |
| `communication_risk_score` | Phase 5 NLP Classifier | Scam probability detected in recent SMS / Call transcripts. | **30%** |
| `behavioral_deviation_score` | Historical Stats ($z$-score) | Amount deviation relative to the user's specific historical spending ($|z| \times 25$, clamped to 100). | **15%** |
| `new_payee_score` | Payee Novelty | $100.0$ if the recipient VPA/payee is first-time/unfamiliar; $0.0$ if known. | **8%** |
| `velocity_score` | Transaction Frequency | Rapid successive transfers within preceding 1 hour: $0$ for 1 txn, $35$ for 2, $70$ for 3, $100$ for $4+$. | **7%** |
| `temporal_correlation_score` | Temporal Correlation Engine | Mathematical proximity between a suspicious communication and the payment attempt. | **5%** |
| **Total** | | | **100%** |

---

## 4. Exact Scoring Formula

The base score is computed as a weighted linear combination:

$$\text{Weighted Score} = \sum_{i=1}^{6} (S_i \times W_i)$$

$$\begin{aligned}
\text{Weighted Score} = &\; (\text{transaction\_anomaly\_score} \times 0.35) \\
&+ (\text{communication\_risk\_score} \times 0.30) \\
&+ (\text{behavioral\_deviation\_score} \times 0.15) \\
&+ (\text{new\_payee\_score} \times 0.08) \\
&+ (\text{velocity\_score} \times 0.07) \\
&+ (\text{temporal\_correlation\_score} \times 0.05)
\end{aligned}$$

---

## 5. Cross-Signal Correlation Boost

A controlled boost of **$+10.0$ points** is applied when compounding threats converge:

$$\text{Final Risk Score} = \min\Big(100.0, \;\max\big(0.0, \;\text{Weighted Score} + \text{Boost}\big)\Big)$$

### Qualification Conditions:
The boost is applied **only when all three conditions are satisfied**:
1. `communication_risk_score` $\ge 60.0$
2. `transaction_anomaly_score` $\ge 60.0$
3. The suspicious communication occurred within $\le 120$ minutes prior to the transaction attempt ($0 \le \Delta t \le 120$).

*If no communication exists, or if communication is older than 2 hours, `boost = 0.0`.*

---

## 6. Temporal Correlation Engine

When a transaction is initiated:
1. The engine inspects the transaction timestamp $t_{\text{txn}}$.
2. It queries `analyzed_messages` for the target `user_id` within a backward window of up to **120 minutes**.
3. **Low-risk communications are ignored** (`classification == 'NORMAL'`, `risk_level == 'LOW'`, or `scam_probability < 30.0`).
4. Proximity factor decays linearly:
   $$\text{Proximity Factor} = 1.0 - \left(\frac{\Delta t}{120.0}\right), \quad \text{where } \Delta t = t_{\text{txn}} - t_{\text{comm}} \text{ (minutes)}$$
   - $\Delta t = 10\text{ min} \implies \text{Proximity} = 0.917$ (*Very Strong*)
   - $\Delta t = 60\text{ min} \implies \text{Proximity} = 0.500$ (*Moderate*)
   - $\Delta t = 119\text{ min} \implies \text{Proximity} = 0.008$ (*Weak*)
   - $\Delta t > 120\text{ min} \implies \text{Proximity} = 0.000$ (*No Correlation*)
5. Temporal Correlation Score:
   $$\text{temporal\_correlation\_score} = \text{Proximity Factor} \times \text{communication\_risk\_score}$$

---

## 7. Discrete Risk Levels & Thresholds

| Score Range | Risk Level | Description | Automated Alert |
|:---:|:---:|---|:---:|
| **$0.0 - 29.0$** | `LOW` | Normal activity matching baseline habits. | No |
| **$30.0 - 59.0$** | `MEDIUM` | Mild anomalies or single isolated warning indicator. | No |
| **$60.0 - 84.0$** | `HIGH` | Significant anomalies or unverified recipient with elevated score. | **Yes (`RISK_FUSION_HIGH`)** |
| **$85.0 - 100.0$** | `CRITICAL` | Converging scam communication and high transaction divergence. | **Yes (`RISK_FUSION_CRITICAL`)** |

---

## 8. Explainability & Guidance System

Elderly users need clear, empathetic, and actionable guidance without technical jargon.

### Standard Guidance:
- **LOW:** *"Continue normally, but remain alert."*
- **MEDIUM:** *"Verify the transaction and communication through official channels."*
- **HIGH:** *"Pause the transaction and verify the recipient and message through an official source."*
- **CRITICAL:** *"Do not proceed. Contact a trusted caregiver or official bank/UPI support using a verified contact method."*

### Top Contributing Factors:
Ranks contributing factors by impact:
- *"Transaction occurred shortly after suspicious communication"*
- *"Suspicious communication detected"*
- *"Unusual transaction amount"*
- *"New or unfamiliar payee"*
- *"Unusual payment frequency"*
- *"Significant behavioral deviation from historical patterns"*
- *"Transaction initiated at an unusual hour"*

---

## 9. Multi-Signal Scenarios

### Scenario A — Normal:
- Regular grocery payment to known shop (₹2,500), no suspicious communication.
- **Score:** $4.8$ $\implies$ `LOW`. No alerts.

### Scenario B — Transaction Anomaly Only:
- High transaction amount (₹35,000) at 11:30 PM to new payee, but no incoming scam messages.
- **Score:** $56.4$ $\implies$ `MEDIUM` (or `HIGH` for extreme amounts).
- Risk driven by transaction anomaly without cross-signal boost.

### Scenario C — Communication Only:
- Scam SMS received (SBI KYC block threat), but no UPI transaction initiated.
- Evaluated independently by Phase 5 NLP; does not fabricate transaction events.

### Scenario D — Correlated Attack:
- Electricity disconnection SMS received 15 minutes before an urgent ₹48,000 transfer to an unfamiliar officer VPA.
- **Score:** $88.0+$ $\implies$ `CRITICAL`.
- Correlation boost ($+10$) applied. Automated critical alert generated.

### Scenario E — Stale Communication:
- Scam SMS received 5 hours ago (300 minutes); unrelated transaction initiated later.
- $\Delta t > 120$ minutes $\implies$ No correlation boost applied.

---

## 10. Database Schema (`risk_events`)

```json
{
  "_id": "67...",
  "id": "re_87f9c2d1b402",
  "event_id": "re_87f9c2d1b402",
  "user_id": "usr_sunita_68",
  "transaction_id": "TXN-UG-928401",
  "communication_id": "msg_scam_01",
  "transaction_anomaly_score": 89.4,
  "communication_risk_score": 96.2,
  "behavioral_deviation_score": 82.0,
  "new_payee_score": 100.0,
  "velocity_score": 70.0,
  "temporal_correlation_score": 95.0,
  "correlation_boost": 10.0,
  "final_risk_score": 97.0,
  "risk_level": "CRITICAL",
  "top_contributing_factors": [
    "Transaction occurred shortly after suspicious communication",
    "Suspicious communication detected",
    "Unusual transaction amount",
    "New or unfamiliar payee"
  ],
  "explanation": "High-risk activity detected because an unusual transaction occurred shortly after a suspicious communication. The transaction involves significant deviations from your normal pattern.",
  "recommended_action": "Do not proceed. Contact a trusted caregiver or official bank/UPI support using a verified contact method.",
  "alert_created": true,
  "created_at": "2026-10-08T20:00:00+00:00",
  "timestamp": "2026-10-08T20:00:00+00:00"
}
```

---

## 11. Security, Privacy & Constraints

1. **No Plaintext Credential Logging:** UPI PINs, OTP codes, card CVVs, and raw SMS texts are masked or referenced by `text_hash` and ID.
2. **Deterministic & Testable:** Clock lookbacks accept explicit timestamps to allow reproducible offline integration tests.
3. **Alert Deduplication:** Checks `transaction_id` in the `alerts` collection prior to creating new alerts, preventing alert fatigue and notification flooding.

---

## 12. Limitations & Future Scope (Phase 7 Roadmap)

1. **Synthetic Base Distribution:** Behavioral baselines are derived from synthetic user profiles and mock banking histories. Production deployment requires historical bank statement aggregation.
2. **Channel Expansion:** Phase 6 correlates SMS and call transcripts. Future phases can incorporate WhatsApp forward links, QR code visual payload extraction, and clipboard monitors.
3. **Phase 7 (Next Step):** Automated Caregiver Notifications (Twilio SMS/Voice integration, emergency freeze workflows, and dashboard telemetry binding).
