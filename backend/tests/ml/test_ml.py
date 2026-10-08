"""UPI Guardian - Comprehensive Machine Learning Test Suite.

Covers all 24 Phase 4 validation requirements:
1. feature extraction
2. z-score calculation
3. zero standard deviation handling
4. velocity calculation
5. new payee detection
6. unusual time detection
7. no NaN/infinite feature values
8. synthetic dataset generation
9. model training
10. model serialization/loading
11. anomaly inference
12. anomaly score range
13. explanation generation
14. normal transaction
15. unusually large transaction
16. new payee transaction
17. unusual-time transaction
18. rapid repeated transaction
19. highly abnormal transaction
20. invalid transaction
21. missing model
22. alert creation
23. duplicate alert prevention
24. API endpoint integration
"""

import math
from pathlib import Path
import tempfile
import numpy as np
import pytest

from app.ml.config import (
    ALERT_TRIGGER_SCORE,
    FEATURE_NAMES,
    MODEL_VERSION,
)
from app.ml.data.synthetic_generator import SyntheticTransactionGenerator
from app.ml.explainability.explainer import BehavioralExplainer
from app.ml.features.extractor import FeatureExtractor
from app.ml.inference.service import AnomalyDetectionService
from app.ml.models.isolation_forest import IsolationForestModel, ModelNotTrainedError
from app.services.transaction_service import TransactionService
from app.utils.errors import ValidationError, ModelNotAvailableError


# =====================================================================
# 1-7. FEATURE EXTRACTION & DATA INTEGRITY TESTS
# =====================================================================

def test_1_feature_extraction():
    """Verify feature extractor outputs a 5-element vector matching FEATURE_NAMES."""
    txn = {
        "amount": 1500.0,
        "payee": "Fresh Basket",
        "upiId": "freshbasket@upi",
        "velocity": 1,
        "time": "10:30 AM",
        "timestamp": "2026-09-15T10:30:00Z",
    }
    stats = {
        "mean": 1400.0,
        "std": 300.0,
        "known_payees": {"Fresh Basket", "freshbasket@upi"},
    }
    features = FeatureExtractor.extract_feature_dict(txn, stats)
    assert set(features.keys()) == set(FEATURE_NAMES)
    assert features["amount"] == 1500.0
    assert abs(features["z_score_deviation"] - round((1500 - 1400) / 300, 4)) < 1e-4
    assert features["velocity"] == 1.0
    assert features["is_new_payee"] == 0.0
    assert features["unusual_time"] == 0.0

    vector = FeatureExtractor.extract_features(txn, stats)
    assert isinstance(vector, np.ndarray)
    assert vector.shape == (5,)


def test_2_z_score_calculation():
    """Verify exact z-score calculation."""
    z = FeatureExtractor.calculate_z_score(amount=3000.0, mean=1000.0, std=500.0)
    assert z == 4.0

    z_below = FeatureExtractor.calculate_z_score(amount=500.0, mean=1000.0, std=500.0)
    assert z_below == -1.0


def test_3_zero_standard_deviation_handling():
    """Verify zero or missing standard deviation returns 0.0 without errors or NaN."""
    # Zero standard deviation
    assert FeatureExtractor.calculate_z_score(amount=2000.0, mean=1000.0, std=0.0) == 0.0

    # Negative standard deviation
    assert FeatureExtractor.calculate_z_score(amount=2000.0, mean=1000.0, std=-10.0) == 0.0

    # None values
    assert FeatureExtractor.calculate_z_score(amount=2000.0, mean=None, std=500.0) == 0.0
    assert FeatureExtractor.calculate_z_score(amount=2000.0, mean=1000.0, std=None) == 0.0


def test_4_velocity_calculation():
    """Verify velocity extraction handles explicit and fallback formats."""
    txn = {"amount": 250, "velocity": 4}
    features = FeatureExtractor.extract_feature_dict(txn)
    assert features["velocity"] == 4.0

    # Invalid string velocity gracefully defaults to 1.0
    txn_bad = {"amount": 250, "velocity": "invalid"}
    features_bad = FeatureExtractor.extract_feature_dict(txn_bad)
    assert features_bad["velocity"] == 1.0


def test_5_new_payee_detection():
    """Verify new payee flag returns 0 for known payee and 1 for unknown."""
    known = {"Fresh Basket", "demo@upi", "Sunita Store"}

    # Known payee name
    assert FeatureExtractor.detect_new_payee("Fresh Basket", "other@upi", known) == 0

    # Known upiId
    assert FeatureExtractor.detect_new_payee("Random Name", "demo@upi", known) == 0

    # Completely unknown
    assert FeatureExtractor.detect_new_payee("Suspicious Crypto Agent", "crypto@fake", known) == 1

    # Explicit flag override
    assert FeatureExtractor.detect_new_payee("Fresh Basket", "demo@upi", known, explicit_flag=True) == 1
    assert FeatureExtractor.detect_new_payee("Unknown", "unknown@upi", known, explicit_flag=False) == 0


def test_6_unusual_time_detection():
    """Verify unusual time detects late night hours (23:00 to 05:00)."""
    # 11:42 PM -> 23:42 -> unusual
    assert FeatureExtractor.detect_unusual_time(time_str="11:42 PM") == 1

    # 02:15 AM -> unusual
    assert FeatureExtractor.detect_unusual_time(time_str="02:15 AM") == 1

    # 10:30 AM -> normal
    assert FeatureExtractor.detect_unusual_time(time_str="10:30 AM") == 0

    # 03:00 PM -> normal
    assert FeatureExtractor.detect_unusual_time(time_str="03:00 PM") == 0

    # ISO timestamp late night
    assert FeatureExtractor.detect_unusual_time(timestamp="2026-09-29T23:30:00Z") == 1
    assert FeatureExtractor.detect_unusual_time(timestamp="2026-09-29T14:30:00Z") == 0


def test_7_no_nan_infinite_feature_values():
    """Verify extractor guarantees strictly finite floats even with corrupted inputs."""
    corrupted_txn = {
        "amount": float("nan"),
        "velocity": float("inf"),
        "payee": None,
        "time": None,
    }
    corrupted_stats = {
        "mean": float("nan"),
        "std": float("inf"),
        "known_payees": None,
    }
    vector = FeatureExtractor.extract_features(corrupted_txn, corrupted_stats)
    assert not np.isnan(vector).any()
    assert not np.isinf(vector).any()
    assert (vector >= -9999.0).all() and (vector <= 9999.0).all()


# =====================================================================
# 8-10. SYNTHETIC DATA & MODEL TRAINING / PERSISTENCE
# =====================================================================

def test_8_synthetic_dataset_generation():
    """Verify synthetic generator generates reproducible dataset with both normal and anomaly records."""
    gen = SyntheticTransactionGenerator(
        num_users=5,
        num_transactions=100,
        anomaly_percentage=0.10,
        random_seed=123,
    )
    df = gen.generate_dataset()
    assert len(df) == 100
    assert (df["is_anomaly"] == 1).sum() == 10
    assert (df["is_anomaly"] == 0).sum() == 90
    for feat in FEATURE_NAMES:
        assert feat in df.columns
        assert not df[feat].isna().any()


def test_9_model_training():
    """Verify Isolation Forest training returns valid summary metrics."""
    gen = SyntheticTransactionGenerator(num_users=5, num_transactions=200, random_seed=42)
    df = gen.generate_dataset()
    X = df[FEATURE_NAMES].to_numpy()

    model = IsolationForestModel(n_estimators=50, contamination=0.10, random_state=42)
    summary = model.train(X)

    assert summary["model_type"] == "IsolationForest"
    assert summary["n_samples"] == 200
    assert summary["n_features"] == 5
    assert summary["anomalies_detected_in_train"] > 0
    assert summary["decision_min"] < summary["decision_max"]


def test_10_model_serialization_loading():
    """Verify model can be saved to disk and loaded without loss of prediction accuracy."""
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / "test_model.joblib"
        meta_path = Path(tmpdir) / "test_meta.json"

        # Train and save
        gen = SyntheticTransactionGenerator(num_users=3, num_transactions=100, random_seed=42)
        X = gen.generate_dataset()[FEATURE_NAMES].to_numpy()

        model_mgr = IsolationForestModel(n_estimators=30, random_state=42)
        model_mgr.train(X)
        model_mgr.save(model_path=model_path, metadata_path=meta_path)

        assert model_path.exists()
        assert meta_path.exists()

        # Clear cache and reload
        IsolationForestModel.clear_cache()
        loaded_model, loaded_meta = IsolationForestModel.load(
            model_path=model_path,
            metadata_path=meta_path,
            force_reload=True,
        )
        assert loaded_meta["model_name"] == "IsolationForest"
        preds = loaded_model.predict(X[:5])
        assert len(preds) == 5


# =====================================================================
# 11-13. INFERENCE & SCORING & EXPLAINABILITY
# =====================================================================

def test_11_anomaly_inference():
    """Verify inference pipeline processes a candidate transaction."""
    service = AnomalyDetectionService()
    result = service.analyze(
        transaction={"amount": 1200, "payee": "City Pharmacy", "velocity": 1, "time": "11:00 AM"},
        historical_stats={"mean": 1100, "std": 300, "known_payees": {"City Pharmacy"}},
    )
    assert "anomaly_score" in result
    assert "anomaly" in result
    assert "risk_level" in result
    assert "features" in result
    assert "explanation" in result
    assert "recommended_action" in result


def test_12_anomaly_score_range():
    """Verify normalized anomaly score is always within [0.0, 100.0]."""
    scores = [
        IsolationForestModel.compute_anomaly_score(-0.35),
        IsolationForestModel.compute_anomaly_score(0.0),
        IsolationForestModel.compute_anomaly_score(0.35),
        IsolationForestModel.compute_anomaly_score(-1.0),
        IsolationForestModel.compute_anomaly_score(1.0),
    ]
    for s in scores:
        assert 0.0 <= s <= 100.0


def test_13_explanation_generation():
    """Verify behavioral explainer produces clear contributing factors and recommended actions."""
    features = {
        "amount": 45000.0,
        "z_score_deviation": 5.2,
        "velocity": 4.0,
        "is_new_payee": 1.0,
        "unusual_time": 1.0,
    }
    stats = {"mean": 2500.0, "std": 800.0}
    exp = BehavioralExplainer.explain(features, anomaly_score=92.0, risk_level="CRITICAL", historical_stats=stats)

    assert exp["recommended_action"] == "block"
    factor_names = [f["factor"] for f in exp["contributing_factors"]]
    assert "amount_deviation" in factor_names
    assert "new_payee" in factor_names
    assert "velocity" in factor_names
    assert "unusual_time" in factor_names
    assert "behavioral_deviation" in factor_names
    assert len(exp["explanation"]) > 20


# =====================================================================
# 14-19. SPECIFIC TRANSACTION BEHAVIOR TESTS
# =====================================================================

def test_14_normal_transaction():
    """Verify typical routine payment is scored with LOW risk."""
    service = AnomalyDetectionService()
    res = service.analyze(
        transaction={
            "amount": 850.0,
            "payee": "Fresh Basket",
            "upiId": "freshbasket@upi",
            "velocity": 1,
            "time": "11:30 AM",
        },
        historical_stats={
            "mean": 1200.0,
            "std": 450.0,
            "known_payees": {"Fresh Basket", "freshbasket@upi"},
        },
    )
    assert res["risk_level"] in ("LOW", "MEDIUM")
    assert res["anomaly_score"] < 50.0
    assert res["recommended_action"] in ("allow", "review")


def test_15_unusually_large_transaction():
    """Verify extreme amount transfer generates high/critical anomaly score."""
    service = AnomalyDetectionService()
    res = service.analyze(
        transaction={
            "amount": 75000.0,
            "payee": "Fresh Basket",
            "velocity": 1,
            "time": "02:00 PM",
        },
        historical_stats={"mean": 1200.0, "std": 450.0, "known_payees": {"Fresh Basket"}},
    )
    assert res["anomaly_score"] > 60.0
    factors = [f["factor"] for f in res["contributing_factors"]]
    assert "amount_deviation" in factors


def test_16_new_payee_transaction():
    """Verify transaction to completely new recipient flags new_payee factor."""
    service = AnomalyDetectionService()
    res = service.analyze(
        transaction={
            "amount": 25000.0,
            "payee": "Unknown Crypto Agency",
            "upiId": "agency@unknown",
            "velocity": 1,
            "time": "03:00 PM",
        },
        historical_stats={"mean": 2000.0, "std": 500.0, "known_payees": {"Apollo Pharmacy"}},
    )
    factors = [f["factor"] for f in res["contributing_factors"]]
    assert "new_payee" in factors


def test_17_unusual_time_transaction():
    """Verify transaction during late night hours triggers unusual_time flag."""
    service = AnomalyDetectionService()
    res = service.analyze(
        transaction={
            "amount": 3500.0,
            "payee": "City Care Pharmacy",
            "time": "02:45 AM",
            "velocity": 1,
        },
        historical_stats={"mean": 2000.0, "std": 500.0, "known_payees": {"City Care Pharmacy"}},
    )
    factors = [f["factor"] for f in res["contributing_factors"]]
    assert "unusual_time" in factors


def test_18_rapid_repeated_transaction():
    """Verify high velocity burst triggers velocity warning."""
    service = AnomalyDetectionService()
    res = service.analyze(
        transaction={
            "amount": 8000.0,
            "payee": "Quick Transfer",
            "velocity": 5,
            "time": "04:15 PM",
        },
        historical_stats={"mean": 2000.0, "std": 500.0, "known_payees": set()},
    )
    factors = [f["factor"] for f in res["contributing_factors"]]
    assert "velocity" in factors


def test_19_highly_abnormal_transaction():
    """Verify combined anomalies (huge amount + new payee + midnight + high velocity) results in CRITICAL or HIGH."""
    service = AnomalyDetectionService()
    res = service.analyze(
        transaction={
            "amount": 85000.0,
            "payee": "Suspicious Overseas Agent",
            "upiId": "agent999@fake",
            "velocity": 6,
            "time": "01:30 AM",
        },
        historical_stats={"mean": 1500.0, "std": 400.0, "known_payees": {"Fresh Basket"}},
    )
    assert res["anomaly_score"] >= 70.0
    assert res["risk_level"] in ("HIGH", "CRITICAL")
    assert res["recommended_action"] in ("review", "block")


# =====================================================================
# 20-24. VALIDATION, ERROR SAFETY & ENDPOINT INTEGRATION
# =====================================================================

def test_20_invalid_transaction_payloads(client):
    """Verify validation returns HTTP 400 for bad payloads."""
    # Zero amount
    res1 = client.post("/api/analyze-transaction", json={"payee": "Shop", "amount": 0, "upiId": "s@upi"})
    assert res1.status_code == 400

    # Negative amount
    res2 = client.post("/api/analyze-transaction", json={"payee": "Shop", "amount": -500, "upiId": "s@upi"})
    assert res2.status_code == 400

    # Missing payee
    res3 = client.post("/api/analyze-transaction", json={"payee": "", "amount": 1000, "upiId": "s@upi"})
    assert res3.status_code == 400

    # Invalid timestamp
    res4 = client.post(
        "/api/analyze-transaction",
        json={"payee": "Shop", "amount": 1000, "upiId": "s@upi", "timestamp": "not-a-timestamp"},
    )
    assert res4.status_code == 400


def test_21_missing_model_handling():
    """Verify clear error is raised if model artifact file is missing."""
    service = AnomalyDetectionService(
        model_path=Path("non_existent_model_dir/missing_weights.joblib"),
        metadata_path=Path("non_existent_model_dir/missing_meta.json"),
    )
    IsolationForestModel.clear_cache()
    with pytest.raises(ModelNotTrainedError):
        service.analyze({"amount": 500, "payee": "Test"})


def test_22_alert_creation_on_threshold(client):
    """Verify high-anomaly transaction creates a pending alert in MongoDB."""
    payload = {
        "transaction_id": "TXN-TEST-ALERT-001",
        "payee": "Unregistered Shadow Agent",
        "amount": 75000,
        "upiId": "shadow@unknown",
        "time": "11:45 PM",
        "velocity": 4,
    }
    response = client.post("/api/analyze-transaction", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["alert"] is not None
    assert data["alert"]["transaction_id"] == "TXN-TEST-ALERT-001"
    assert data["alert"]["status"] == "pending"
    assert data["alert"]["level"] in ("high", "critical")


def test_23_duplicate_alert_prevention(client):
    """Verify retrying the exact same analysis request does not create duplicate alerts."""
    payload = {
        "transaction_id": "TXN-TEST-IDEMPOTENT-999",
        "payee": "Unknown Beneficiary",
        "amount": 80000,
        "upiId": "beneficiary@fake",
        "time": "01:20 AM",
        "velocity": 5,
    }
    res1 = client.post("/api/analyze-transaction", json=payload)
    data1 = res1.get_json()
    alert1 = data1["alert"]
    assert alert1 is not None

    # Retry with exact same transaction_id
    res2 = client.post("/api/analyze-transaction", json=payload)
    data2 = res2.get_json()
    alert2 = data2["alert"]
    assert alert2 is not None

    # Must return the same existing alert id without creating duplicates
    assert alert1["id"] == alert2["id"]


def test_24_api_endpoint_integration(client):
    """Verify full end-to-end integration through Flask REST endpoint."""
    payload = {
        "payee": "MahaVitaran Electricity",
        "amount": 1850,
        "upiId": "mahavitaran@billdesk",
        "location": "Pune",
        "device": "Sunita's phone",
        "time": "10:15 AM",
    }
    response = client.post("/api/analyze-transaction", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "transaction_id" in data
    assert "analysis" in data
    assert "anomaly_score" in data["analysis"]
    assert "features" in data["analysis"]
    assert data["analysis"]["features"]["amount"] == 1850.0
    assert "contributing_factors" in data["analysis"]
    assert "explanation" in data["analysis"]
