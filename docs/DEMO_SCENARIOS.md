# UPI Guardian — Live Demonstration Scenarios & Test Scripts

**Purpose**: Standardized demonstration protocol for evaluators, project vivas, and interactive testing.  
**Data Policy**: Uses **100% synthetic demonstration data**. No real personal names, real bank accounts, or real phone numbers are utilized.  

---

## Demonstration Setup

- **Demo Elder Identity**: `Sunita Devi` (`usr_sunita_68` / `sunita@demo.upiguardian.org`)
- **Demo Caregiver Identity**: `Rohit Sharma` (Son) (`cg_son_rohit` / `+91 98765 43210`)
- **Mode Toggle**: Tested across standard mode and **Senior Mode** (large fonts, 48px touch targets).

---

## Scenario 1: Low Risk (Routine Daily Payment)

### Context & Inputs
- **Payee**: `Mother Dairy Booth 41` (`motherdairy@okhdfcbank`)
- **Amount**: ₹250.00
- **Transaction History**: Routine morning transaction (15+ prior payments)
- **Time of Day**: 08:30 AM (Regular hours)
- **Communication Signals**: None (no recent scam messages)

### System Processing
1. **Isolation Forest**: Identifies standard amount, frequent payee, normal velocity $\implies$ Anomaly Score: $0.12$.
2. **NLP Classifier**: No suspicious communication found $\implies$ Scam Score: $0.00$.
3. **Risk Fusion Engine**:
   $$\text{Score} = (0.35 \times 12) + (0.35 \times 0) + (0.15 \times 0) + (0.15 \times 10) = 5.7 / 100$$
4. **Classification**: `LOW` Risk.

### Expected Demonstration Outcome
- **UI State**: Green "✓ Safe" badge displayed.
- **Elder Advisory**: *"Transaction appears safe and matches your typical spending patterns."*
- **Escalation**: Zero caregiver alerts dispatched. No SMS or voice calls.

---

## Scenario 2: Medium Risk (Unfamiliar Merchant / Moderate Value)

### Context & Inputs
- **Payee**: `QuickFix Electrical Services` (`quickfix.pune@upi`)
- **Amount**: ₹12,500.00
- **Transaction History**: First-time payee (`is_new_payee = true`)
- **Time of Day**: 03:15 PM (Daytime)
- **Communication Signals**: None

### System Processing
1. **Isolation Forest**: Moderately elevated transaction value, unknown payee $\implies$ Anomaly Score: $0.48$.
2. **NLP Classifier**: No scam context detected $\implies$ Scam Score: $0.00$.
3. **Risk Fusion Engine**:
   $$\text{Score} = (0.35 \times 48) + (0.35 \times 0) + (0.15 \times 80) + (0.15 \times 20) = 31.8 / 100$$
4. **Classification**: `MEDIUM` Risk.

### Expected Demonstration Outcome
- **UI State**: Yellow "⚠ Please Review" badge displayed.
- **Elder Advisory**: *"This is an unfamiliar merchant with a moderately high payment amount. Please double check that you know this person before entering your PIN."*
- **Escalation**: Logged in dashboard alerts; no automated caregiver emergency dispatch.

---

## Scenario 3: High Risk (Large Payment + Phishing Communication)

### Context & Inputs
- **Communication Context**: Inbound SMS 45 minutes prior:
  > *"Dear customer, electricity bill pending. Power will be disconnected tonight. Pay immediately to avoid penalty."*
- **Payee**: `Power Bill Collection Unit` (`mahadiscom.support@ybl`)
- **Amount**: ₹38,000.00
- **Transaction History**: Brand new payee, 4x higher than standard monthly electric bill
- **Time of Day**: 06:45 PM

### System Processing
1. **NLP Classifier**: Scans SMS text $\implies$ Scam Probability: $0.84$ (Flags `electricity_bill`, `disconnected`, `penalty`).
2. **Isolation Forest**: High value, unfamiliar payee $\implies$ Anomaly Score: $0.72$.
3. **Risk Fusion Engine**:
   $$\text{Score} = (0.35 \times 72) + (0.35 \times 84) + (0.15 \times 100) + (0.15 \times 50) = 77.1 / 100$$
4. **Classification**: `HIGH` Risk.

### Expected Demonstration Outcome
- **UI State**: High-visibility Orange "! High Risk" banner.
- **Elder Advisory**: *"Caution: High-risk activity detected. This payment closely follows a suspicious message concerning bill disconnection."*
- **Escalation Service**: Triggers **SMS alert** to designated caregiver Rohit Sharma:
  > *"UPI Guardian Alert: High-risk transaction of ₹38,000 flagged for Sunita Devi to Power Bill Collection Unit."*
- **Twilio Dispatch**: Mock SMS dispatched (`SM_MOCK_*`); logged in notification telemetry.

---

## Scenario 4: Critical Risk (Urgent Scam Call + Late-Night Fund Transfer)

### Context & Inputs
- **Communication Context**: Automated voice call transcript 8 minutes prior:
  > *"This is bank fraud department officer. Your bank account is locked due to suspicious activity. Share OTP and immediately transfer ₹75,000 to safety verification account to secure your pension."*
- **Payee**: `Reserve Safe Custody Acct` (`safe.audit.pension@axl`)
- **Amount**: ₹75,000.00
- **Transaction History**: First-time individual payee, exceeds 99th percentile of Sunita's payment amounts
- **Time of Day**: 11:45 PM (Severe late-night deviation, quiet hours)

### System Processing
1. **NLP Classifier**: Call transcript scanned $\implies$ Scam Probability: $0.96$ (Flags `bank_fraud`, `account_locked`, `safety_verification`, `pension`).
2. **Isolation Forest**: Severe behavioral anomaly, unusual late hour $\implies$ Anomaly Score: $0.94$.
3. **Cross-Signal Correlation Engine**:
   - Communication occurred 8 minutes prior ($< 15\text{ min}$ window).
   - Both NLP score ($0.96 \ge 0.65$) and anomaly score ($0.94 \ge 0.60$) cross critical thresholds.
   - **Temporal Correlation Boost Applied**: $+10.0$ points.
4. **Fused Risk Score**:
   $$\text{Raw Score} = (0.35 \times 94) + (0.35 \times 96) + (0.15 \times 100) + (0.15 \times 100) = 96.5$$
   $$\text{Final Fused Score} = \min(100.0, 96.5 + 10.0) = 100.0 / 100$$
5. **Classification**: `CRITICAL` Risk.

### Expected Demonstration Outcome
- **UI State**: Full-screen Red Alert overlay: "✕ Possible Scam Detected".
- **Elder Advisory**: *"STOP IMMEDIATELY: Bank officials never ask for transfers to 'safe accounts'. Contact your son Rohit or your local bank branch directly."*
- **Escalation Service**:
  - Triggers **immediate SMS notification** to Rohit Sharma.
  - Triggers **immediate automated Voice Emergency Call** to Rohit Sharma.
  - Bypasses quiet-hours restrictions due to `CRITICAL` classification.
- **Caregiver Emergency Acknowledgement**:
  - Rohit opens caregiver dashboard, clicks **"Acknowledge & Mark Safe"**.
  - Database status transitions from `PENDING` to `ACKNOWLEDGED`.
- **Deduplication Check**:
  - Repeated simulated calls for the same event produce zero duplicate alerts.
