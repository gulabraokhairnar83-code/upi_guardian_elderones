# UPI Guardian — Phase 4: Machine Learning Transaction Anomaly Detection Engine

## Overview & Architecture

UPI Guardian protects elderly Indian UPI users from coercive digital transactions and cyber-fraud scams. In Phase 4, the transaction monitoring subsystem was upgraded from a static development stub to a machine learning behavioral anomaly detection engine using scikit-learn's **Isolation Forest** (`IsolationForest`).

```
Candidate Transaction (POST /api/analyze-transaction)
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  Request Validation & Normalization                    │
│  (Validates payee, positive amount, UPI ID, timestamp) │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Historical Context Retrieval (MongoDB)               │
│  (Calculates user mean, std, known payees, velocity)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Feature Extraction Pipeline (5 Numerical Features)    │
│  [amount, z_score_deviation, velocity, new_payee, time]│
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Isolation Forest Inference Engine                     │
│  (Pre-trained joblib model, singleton cached)         │
│  raw decision_function -> Normalized Anomaly Score     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Behavioral Explainability Layer                       │
│  (Factor breakdown: amount, velocity, new payee, time) │
│  Recommended action: allow / review / block            │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Persistence & Idempotent Alerting (MongoDB)           │
│  • Insert transaction into 'transactions' collection   │
│  • Record event in 'risk_events'                       │
│  • Create alert in 'alerts' (deduplicated by txn_id)   │
└────────────────────────────────────────────────────────┘
```

---

## 1. Why Isolation Forest was Selected

1. **Unsupervised Outlier Isolation**: Elder transaction histories predominantly consist of normal, routine payments (groceries, medicine, utility bills). Verified fraud instances are rare and continuously evolving. Isolation Forest does not require labeled fraud data to identify behavioral anomalies.
2. **Sub-Sampling & Computational Efficiency**: Isolation Forest constructs isolation trees ($iTrees$) with sub-sampled partitions. Anomaly instances have short path lengths because their extreme or unusual attribute combinations require few random hyper-plane splits to isolate.
3. **Low Latency for Real-Time UPI Flows**: Inference requires traversing small binary trees ($O(t \cdot \log \psi)$ where $t$ is the number of trees and $\psi$ is the subsample size), executing in under 2 milliseconds on standard CPU hardware.
4. **Resilience to Swamping and Masking**: By isolating anomalies rather than measuring normal cluster densities, Isolation Forest avoids the swamping and masking issues common to distance-based methods like k-NN or Local Outlier Factor (LOF).

---

## 2. What Isolation Forest Does

Isolation Forest explicitly isolates anomalous instances rather than profiling normal points.
- A random feature is selected between its minimum and maximum values.
- A random split value is chosen recursively.
- Anomalies typically separate closer to the root of the tree (shorter average path length $h(x)$).
- scikit-learn's `decision_function(X)` produces a centered anomaly score where:
  - $s(x) < 0$: Anomaly (inlier/outlier decision boundary at $0.0$).
  - $s(x) \ge 0$: Normal inlier.

---

## 3. Synthetic Training Dataset Generation

To establish an elder-demographic behavioral baseline, a reproducible synthetic data generator was implemented in [`backend/app/ml/data/synthetic_generator.py`](file:///c:/Users/Dell/Documents/UPI%20Guardian/backend/app/ml/data/synthetic_generator.py):

### Supported Spending Categories
1. **Groceries**: ₹150 – ₹2,500 (mean ₹950, std ₹400)
2. **Medicines**: ₹200 – ₹4,000 (mean ₹1,400, std ₹600)
3. **Electricity bills**: ₹800 – ₹3,500 (mean ₹1,800, std ₹500)
4. **Mobile recharge**: ₹199 – ₹800 (mean ₹399, std ₹150)
5. **Gas cylinder**: ₹750 – ₹1,300 (mean ₹950, std ₹150)
6. **Rent**: ₹8,000 – ₹22,000 (mean ₹14,000, std ₹3,000)
7. **Family transfers**: ₹500 – ₹8,000 (mean ₹3,000, std ₹1,500)
8. **Shopping**: ₹300 – ₹3,500 (mean ₹1,200, std ₹700)
9. **Utility payments**: ₹300 – ₹2,000 (mean ₹850, std ₹350)

### Configurable Generation Parameters
- `num_users`: Number of distinct elder user profiles (default: 15)
- `num_transactions`: Total transactions generated (default: 1,200)
- `anomaly_percentage`: Contamination proportion (default: 0.08 / 8.0%)
- `random_seed`: Seed for deterministic reproducibility (default: 42)

### Diversified Anomaly Profiles
- **Extreme Amount Spike**: ₹35,000 – ₹92,000 transferred to unverified shadow accounts.
- **Velocity Burst**: 4 to 7 repeated payments within a 1-hour window.
- **Urgent Midnight Transfer**: ₹18,000 – ₹55,000 transacted between 11:00 PM and 5:00 AM.
- **Extreme Z-Score Transfer**: Deviations of 5.5 to 12.0 standard deviations from user baseline.
- **Multi-Factor Suspicious Pattern**: High amount + new payee + midnight + elevated velocity.

---

## 4. Feature Engineering & Definitions

The feature extraction pipeline in [`backend/app/ml/features/extractor.py`](file:///c:/Users/Dell/Documents/UPI%20Guardian/backend/app/ml/features/extractor.py) extracts exactly 5 numerical features:

| Feature Name | Type | Range | Description & Calculation |
| :--- | :--- | :--- | :--- |
| `amount` | `float` | $[0.0, \infty)$ | Transaction value in Indian Rupees (INR). Validated positive and finite. |
| `z_score_deviation` | `float` | $(-\infty, \infty)$ | $(amount - \mu_{historical}) / \sigma_{historical}$. Safely returns `0.0` if $\sigma \le 0$ or history is missing. |
| `velocity` | `float` | $[1.0, \infty)$ | Number of transactions initiated within the preceding 1-hour window. |
| `is_new_payee` | `float` | $\{0.0, 1.0\}$ | Binary indicator: `0` = known payee from user history, `1` = recipient never transacted before. |
| `unusual_time` | `float` | $\{0.0, 1.0\}$ | Binary indicator: `1` if transaction occurred during late-night hours (23:00 to 05:00), else `0`. |

### Zero Standard Deviation and Missing History Safety
- If a user has only 1 transaction or all historical transactions have identical amounts ($\sigma = 0$), `calculate_z_score` returns `0.0`.
- All vectors pass through `np.nan_to_num(vector, nan=0.0, posinf=9999.0, neginf=-9999.0)` guaranteeing that no `NaN` or `Inf` values can reach the model.

---

## 5. Model Hyperparameters & Training

- **Algorithm**: `sklearn.ensemble.IsolationForest`
- **Number of Estimators (`n_estimators`)**: `150`
- **Contamination Rate (`contamination`)**: `0.08` (8.0%)
- **Random State (`random_state`)**: `42`
- **Bootstrap**: `False`
- **Model Version**: `1.0.0`
- **Output Artifacts**:
  - Weights: `backend/app/ml/models/artifacts/isolation_forest_v1.joblib`
  - Metadata: `backend/app/ml/models/artifacts/metadata.json`

### Training Script
Model training is executed via:
```powershell
python scripts/train_anomaly_model.py --transactions 1200 --contamination 0.08 --seed 42
```
Training summary metrics:
- Number of records: 1,200
- Features: 5 (`amount`, `z_score_deviation`, `velocity`, `is_new_payee`, `unusual_time`)
- Contamination: 0.08
- Detected anomalies in train set: 96 (8.00%)
- Decision score range: `[-0.1907, 0.2427]`, mean: `0.1548`

---

## 6. Anomaly Score Calibration (0–100 Scale)

In scikit-learn Isolation Forest, `decision_function(X)` returns:
- $s(X) < 0$ for anomalous points
- $s(X) \ge 0$ for normal points

To translate raw decision function outputs into a user-friendly application score where **higher score means more anomalous**:

```python
if raw_decision < 0:
    score = 50.0 + (-raw_decision * 260.0)
else:
    score = 50.0 - (raw_decision * 200.0)
anomaly_score = max(0.0, min(100.0, score))
```

### Risk Level Mapping (Transaction Anomaly Risk)
- `0.0` to `30.0`: **`LOW`** (Frontend status: `safe`)
- `30.1` to `60.0`: **`MEDIUM`** (Frontend status: `review`)
- `60.1` to `85.0`: **`HIGH`** (Frontend status: `high`)
- `85.1` to `100.0`: **`CRITICAL`** (Frontend status: `critical`)

> [!IMPORTANT]
> This score represents **Transaction Anomaly Risk** based on behavioral deviations. It is **NOT** a confirmed fraud verdict or a fraud probability. Final comprehensive risk will be synthesized in Phase 6 combining NLP and communications telemetry.

---

## 7. Explainability Layer (`BehavioralExplainer`)

Because Isolation Forest does not natively output individual feature importance for a single sample, an application-level explainability layer evaluates domain rules:
- **`amount_deviation`**: Flags if $z \ge 1.75$ (MEDIUM) or $z \ge 3.0$ (HIGH/CRITICAL).
- **`new_payee`**: Flags if the payee is unknown to the user.
- **`velocity`**: Flags if frequency $\ge 3$ transactions in 1 hour.
- **`unusual_time`**: Flags late-night payments (11:00 PM – 5:00 AM).
- **`behavioral_deviation`**: Flags compound multi-signal risk when $\ge 2$ factors co-occur with an anomaly score $\ge 60$.

Each factor includes:
```json
{
  "factor": "amount_deviation",
  "value": 75000.0,
  "severity": "CRITICAL",
  "message": "Transaction amount of ₹75,000.00 is exceptionally higher than the user's historical average of ₹2,850.00 (z-score: 64.42)."
}
```

---

## 8. Database Integration & Idempotent Alerting

When `POST /api/analyze-transaction` executes:
1. Analyzed record is stored in `transactions` with all 17 schema fields. If the same `transaction_id` is re-analyzed, it updates the record rather than causing MongoDB duplicate key errors.
2. If `anomaly_score >= 60.0` or `risk_level in ("HIGH", "CRITICAL")`:
   - Checks `alerts.find_one({"transaction_id": txn_id})`.
   - If alert does not exist, inserts a new alert with auto-incrementing ID.
   - If alert already exists, returns the existing alert to prevent duplicate notifications.
   - Inserts incident timeline entry into `risk_events`.

---

## 9. Error Handling & Model Safety

- **Missing Model Artifact**: If `isolation_forest_v1.joblib` is deleted or missing, the service raises `ModelNotAvailableError` (HTTP 503). It **never falls back to fake ML predictions**.
- **Malformed Payloads**: Zero, negative, NaN amounts, or invalid timestamps return HTTP 400 with descriptive error messages.
- **Singleton Model Caching**: `IsolationForestModel.load()` caches the estimator in memory with a thread lock so the model is not re-read from disk on every API call.
