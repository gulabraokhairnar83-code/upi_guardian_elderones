# UPI Guardian — Phase 5: NLP Scam Communication Analyzer (SMS + Call Transcript Detection)

## Overview & Architecture

UPI Guardian protects elderly Indian UPI users from coercive digital transactions and cyber-fraud scams. In Phase 5, an independent **NLP Scam Communication Analyzer** was implemented to detect social engineering and coercive extortion patterns in **SMS messages** and **phone call transcripts**.

```
SMS / Call Transcript (POST /api/analyze-message)
                       │
                       ▼
┌────────────────────────────────────────────────────────┐
│  Text Preprocessing & Privacy Sanitization             │
│  (URL/phone normalization, lowercase, SHA-256 hash)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  TF-IDF Feature Transformation                         │
│  (Unigram + Bigram vocabulary, sublinear TF scaling)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Multi-Class Logistic Regression Inference             │
│  Classes: NORMAL, SUSPICIOUS, SCAM                     │
│  Predicts class probabilities -> Scam Probability %    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Rule-Based Linguistic Explainability Layer            │
│  (Detects 14 scam categories & suspicious phrases)     │
│  Generates elder-friendly advice & safety actions      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  MongoDB Audit Logging & Idempotent Alerting           │
│  • Deduplicated record in 'analyzed_messages'          │
│  • Alert in 'alerts' collection if risk >= 50%         │
└────────────────────────────────────────────────────────┘
```

---

## 1. Problem Definition

Elderly UPI users are frequently targeted by coercive social engineering scams via SMS and telephone calls:
- Threat of immediate power disconnection (MSEB scam)
- Fake bank KYC expiration or SIM card deactivation
- Fake police/court emergency impersonation of family members
- Deceptive remote access installations (AnyDesk, TeamViewer)
- Reverse QR code / UPI PIN entry scams for fake prizes or refunds

The goal of this subsystem is to provide an independent, transparent **NLP Communication Risk Signal** before financial transactions are authorized.

---

## 2. Dataset Design & Classes

Implemented in [`backend/app/nlp/data/dataset.py`](file:///c:/Users/Dell/Documents/UPI%20Guardian/backend/app/nlp/data/dataset.py):
- **Classes**: `NORMAL`, `SUSPICIOUS`, `SCAM`.
- **Benign Counter-Examples**: Legitimate messages containing words like `"OTP"`, `"verification"`, `"account"`, and `"payment"` were deliberately included to prevent the model from treating benign security notices as scams.
- **Augmentation**: Variations across bank names (SBI, HDFC, ICICI, Axis), amounts (₹1,250 – ₹75,000), and deadlines (10 minutes, tonight at 9:30 PM, within 24 hours).

### Supported Scam Categories (14 Categories)
1. `OTP_REQUEST`: Urgent requests to share or verify 6-digit OTPs.
2. `UPI_PIN_REQUEST`: Coercive claims that UPI PIN is required to receive incoming refunds/funds.
3. `KYC_THREAT`: False claims of expired KYC or account freezes within hours.
4. `ACCOUNT_BLOCK_THREAT`: Warnings of imminent account suspension or debit card cancellation.
5. `URGENT_PAYMENT`: Emergency extortion citing police arrest or hospital custody.
6. `FAKE_BANK_SUPPORT`: Impersonation of bank fraud cell or security manager.
7. `FAKE_UPI_SUPPORT`: Claims from Google Pay/PhonePe/Paytm support regarding failed refunds.
8. `PRIZE_REWARD_SCAM`: Lottery/KBC lucky draw prizes requiring registration/processing fees.
9. `IMPERSONATION`: Impersonating police inspectors, telecom officers, or a child's friend.
10. `REMOTE_ACCESS_REQUEST`: Demanding installation of AnyDesk, TeamViewer, QuickSupport, or APK files.
11. `SUSPICIOUS_PAYMENT_LINK`: Obfuscated or shortened links (`bit.ly`, `tinyurl`) to phishing pages.
12. `ELECTRICITY_DISCONNECTION_SCAM`: Threats of power cuts tonight unless an immediate fee is paid.
13. `LOAN_OR_REFUND_SCAM`: Unsolicited pre-approved loans, tax refunds, or lapsed policy bonuses.
14. `DELIVERY_OR_CUSTOMS_SCAM`: Fabricated customs penalties or courier address verification fees.

---

## 3. Text Preprocessing & Privacy

Implemented in [`backend/app/nlp/preprocessing/text_cleaner.py`](file:///c:/Users/Dell/Documents/UPI%20Guardian/backend/app/nlp/preprocessing/text_cleaner.py):
- **URL Normalization**: Standardizes `https://...` and `bit.ly/...` into `link_url`.
- **Phone Normalization**: Standardizes Indian phone patterns into `phone_num`.
- **Punctuation & Space Normalization**: Cleans noise characters while preserving hyphens and meaningful terms.
- **Privacy Hashing**: Uses SHA-256 (`text_hash`) to identify duplicate messages without storing plain text in memory or indexes.
- **Log Masking**: Masks 4–6 digit OTPs and phone numbers in any diagnostic logs.

---

## 4. Feature Extraction & Classifier

- **Feature Representation**: `scikit-learn` `TfidfVectorizer`
  - Unigram and bigram features (`ngram_range=(1, 2)`)
  - Sublinear TF scaling enabled
  - Maximum features: 2,500
- **Classifier**: `LogisticRegression`
  - Multinomial multi-class formulation
  - `class_weight='balanced'`
  - `random_state=42`, `C=2.0`
- **Output Artifacts**:
  - `backend/app/nlp/models/artifacts/tfidf_vectorizer.joblib`
  - `backend/app/nlp/models/artifacts/scam_classifier.joblib`
  - `backend/app/nlp/models/artifacts/metadata.json`

---

## 5. Risk Scoring & Calibration (0–100 Scale)

The classifier outputs class probabilities ($P_{normal}, P_{suspicious}, P_{scam}$). A normalized scam probability estimate is synthesized:

$$\text{scam\_probability} = \min(100.0, (P_{scam} \times 100.0) + (P_{suspicious} \times 45.0))$$

### Risk Levels (NLP Communication Risk)
- `0.0` to `24.0`: **`LOW`** (safe)
- `25.0` to `49.0`: **`MEDIUM`** (review)
- `50.0` to `74.0`: **`HIGH`** (high)
- `75.0` to `100.0`: **`CRITICAL`** (critical)

> [!NOTE]
> This score represents **NLP Communication Risk** based on linguistic coercion patterns. It is **NOT** a final fraud verdict. Final multi-signal risk fusion combining both transaction behavioral telemetry and NLP risk will occur in Phase 6.

---

## 6. Explainability Layer (`ScamExplainer`)

Isolation of ML prediction from domain explanations:
- **ML Layer**: Predicts probability and statistical classification.
- **Rule Layer**: Evaluates regex patterns for the 14 scam categories and extracts suspicious phrases.
- **Actionable Guidance**:
  - `NORMAL`: "Continue normally. Remember to never disclose your UPI PIN or banking passwords."
  - `SUSPICIOUS`: "Do not share personal details, OTP, or UPI PIN. Verify the sender's identity using an independent official contact method."
  - `SCAM`: "Do not respond, click links, share OTP/PIN, or transfer money. Contact your bank through its official verified customer care number."

---

## 7. MongoDB Persistence & Deduplication

- Collection: `analyzed_messages`
- Schema Fields: `id`, `user_id`, `message_type`, `text_hash`, `classification`, `scam_probability`, `risk_level`, `categories`, `suspicious_phrases`, `explanation`, `recommended_action`, `model_version`, `analyzed_at`.
- **Idempotency**: Submitting identical text with the same user ID updates the existing record rather than creating duplicate documents.
- **Alert Deduplication**: If `scam_probability >= 50.0`, an alert (`SCAM_COMMUNICATION`) is inserted into `alerts` deduplicated by `text_hash`.

---

## 8. Limitations & Future Work

1. **Synthetic Training Baseline**: Evaluation metrics reflect synthetic and legal demonstration examples, not live telecom carrier traffic.
2. **Multilingual Expansion**: Current implementation focuses on English and Romanized Hinglish. Future iterations can incorporate native Devanagari script NLP models.
3. **Multi-Signal Integration**: Standalone NLP risk will be combined with transaction telemetry in Phase 6 (Risk Fusion Engine).
