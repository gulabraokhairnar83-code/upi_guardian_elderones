"""UPI Guardian - Phase 6 Risk Fusion Engine Test Suite.

Covers all 32 required test scenarios:
1. Weight configuration
2. Score normalization
3. Score clamping
4. LOW risk classification
5. MEDIUM risk classification
6. HIGH risk classification
7. CRITICAL risk classification
8. Transaction-only risk
9. Communication-only risk
10. Combined transaction + communication risk
11. New payee signal
12. Velocity signal
13. Behavioral deviation signal
14. Temporal correlation within 2 hours
15. Temporal correlation outside 2 hours
16. Strong correlation
17. No communication available
18. Normal communication ignored
19. Correlation boost applied
20. Maximum score remains 100
21. Explainability output
22. Top contributing factors
23. Recommended action
24. Risk event persistence
25. Alert creation
26. Alert deduplication
27. API request validation
28. API response schema
29. Missing transaction handling
30. Missing communication handling
31. Phase 4 Isolation Forest compatibility
32. Phase 5 NLP Scam Detection compatibility
"""

from datetime import datetime, timedelta, timezone
import pytest
from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.message_repository import MessageRepository
from app.db.repositories.risk_event_repository import RiskEventRepository
from app.db.repositories.transaction_repository import TransactionRepository
from app.risk_fusion.config import RiskFusionConfig
from app.risk_fusion.correlation import TemporalCorrelationEngine
from app.risk_fusion.explainer import RiskFusionExplainer
from app.risk_fusion.inference import RiskFusionService
from app.risk_fusion.models import RiskSignals
from app.risk_fusion.scoring import RiskScoringEngine
from app.utils.errors import NotFoundError, ValidationError


# ------------------------------------------------------------------------------
# 1. Weight Configuration
# ------------------------------------------------------------------------------
def test_1_weight_configuration():
    weights = [
        RiskFusionConfig.WEIGHT_TRANSACTION_ANOMALY,
        RiskFusionConfig.WEIGHT_COMMUNICATION_RISK,
        RiskFusionConfig.WEIGHT_BEHAVIORAL_DEVIATION,
        RiskFusionConfig.WEIGHT_NEW_PAYEE,
        RiskFusionConfig.WEIGHT_VELOCITY,
        RiskFusionConfig.WEIGHT_TEMPORAL_CORRELATION,
    ]
    assert pytest.approx(sum(weights), 0.001) == 1.00
    assert RiskFusionConfig.WEIGHT_TRANSACTION_ANOMALY == 0.35
    assert RiskFusionConfig.WEIGHT_COMMUNICATION_RISK == 0.30
    assert RiskFusionConfig.WEIGHT_BEHAVIORAL_DEVIATION == 0.15
    assert RiskFusionConfig.WEIGHT_NEW_PAYEE == 0.08
    assert RiskFusionConfig.WEIGHT_VELOCITY == 0.07
    assert RiskFusionConfig.WEIGHT_TEMPORAL_CORRELATION == 0.05


# ------------------------------------------------------------------------------
# 2. Score Normalization
# ------------------------------------------------------------------------------
def test_2_score_normalization():
    # Transaction anomaly (0-100 or 0-1)
    assert RiskScoringEngine.normalize_transaction_anomaly(0.75) == 75.0
    assert RiskScoringEngine.normalize_transaction_anomaly(85.0) == 85.0
    assert RiskScoringEngine.normalize_transaction_anomaly(None) == 0.0

    # Communication risk
    assert RiskScoringEngine.normalize_communication_risk(0.92) == 92.0
    assert RiskScoringEngine.normalize_communication_risk(60.0) == 60.0

    # Behavioral deviation (z-score)
    assert RiskScoringEngine.normalize_behavioral_deviation(2.0) == 50.0  # 2.0 * 25
    assert RiskScoringEngine.normalize_behavioral_deviation(4.0) == 100.0  # clamped to 100
    assert RiskScoringEngine.normalize_behavioral_deviation(75.0) == 75.0  # already scaled

    # New payee
    assert RiskScoringEngine.normalize_new_payee(True) == 100.0
    assert RiskScoringEngine.normalize_new_payee(False) == 0.0
    assert RiskScoringEngine.normalize_new_payee(1.0) == 100.0
    assert RiskScoringEngine.normalize_new_payee(0.0) == 0.0

    # Velocity
    assert RiskScoringEngine.normalize_velocity(1.0) == 0.0
    assert RiskScoringEngine.normalize_velocity(2.0) == 35.0
    assert RiskScoringEngine.normalize_velocity(3.0) == 70.0
    assert RiskScoringEngine.normalize_velocity(4.0) == 100.0


# ------------------------------------------------------------------------------
# 3. Score Clamping
# ------------------------------------------------------------------------------
def test_3_score_clamping():
    assert RiskScoringEngine.clamp_score(-20.0) == 0.0
    assert RiskScoringEngine.clamp_score(150.0) == 100.0
    assert RiskScoringEngine.clamp_score(float("nan")) == 0.0
    assert RiskScoringEngine.clamp_score(float("inf")) == 0.0
    assert RiskScoringEngine.clamp_score(45.5) == 45.5


# ------------------------------------------------------------------------------
# 4. LOW Risk Classification (0 - 29)
# ------------------------------------------------------------------------------
def test_4_low_risk_classification():
    assert RiskFusionConfig.determine_risk_level(0.0) == "LOW"
    assert RiskFusionConfig.determine_risk_level(15.0) == "LOW"
    assert RiskFusionConfig.determine_risk_level(29.0) == "LOW"


# ------------------------------------------------------------------------------
# 5. MEDIUM Risk Classification (30 - 59)
# ------------------------------------------------------------------------------
def test_5_medium_risk_classification():
    assert RiskFusionConfig.determine_risk_level(29.5) == "MEDIUM"
    assert RiskFusionConfig.determine_risk_level(45.0) == "MEDIUM"
    assert RiskFusionConfig.determine_risk_level(59.0) == "MEDIUM"


# ------------------------------------------------------------------------------
# 6. HIGH Risk Classification (60 - 84)
# ------------------------------------------------------------------------------
def test_6_high_risk_classification():
    assert RiskFusionConfig.determine_risk_level(60.0) == "HIGH"
    assert RiskFusionConfig.determine_risk_level(72.0) == "HIGH"
    assert RiskFusionConfig.determine_risk_level(84.0) == "HIGH"


# ------------------------------------------------------------------------------
# 7. CRITICAL Risk Classification (85 - 100)
# ------------------------------------------------------------------------------
def test_7_critical_risk_classification():
    assert RiskFusionConfig.determine_risk_level(85.0) == "CRITICAL"
    assert RiskFusionConfig.determine_risk_level(95.0) == "CRITICAL"
    assert RiskFusionConfig.determine_risk_level(100.0) == "CRITICAL"


# ------------------------------------------------------------------------------
# 8. Transaction-Only Risk (Scenario B)
# ------------------------------------------------------------------------------
def test_8_transaction_only_risk():
    signals = RiskSignals(
        transaction_anomaly_score=85.0,
        communication_risk_score=0.0,
        behavioral_deviation_score=60.0,
        new_payee_score=0.0,
        velocity_score=35.0,
        temporal_correlation_score=0.0,
    )
    weighted = RiskScoringEngine.compute_weighted_score(signals)
    # Expected: 85*0.35 + 0 + 60*0.15 + 0 + 35*0.07 + 0 = 29.75 + 9.0 + 2.45 = 41.2
    assert pytest.approx(weighted, 0.5) == 41.2
    # No boost since communication risk is 0
    final, boost = RiskScoringEngine.apply_cross_signal_boost(signals, weighted, delta_minutes=None)
    assert boost == 0.0
    assert final == weighted


# ------------------------------------------------------------------------------
# 9. Communication-Only Risk (Scenario C)
# ------------------------------------------------------------------------------
def test_9_communication_only_risk():
    signals = RiskSignals(
        transaction_anomaly_score=15.0,
        communication_risk_score=90.0,
        behavioral_deviation_score=0.0,
        new_payee_score=0.0,
        velocity_score=0.0,
        temporal_correlation_score=0.0,
    )
    weighted = RiskScoringEngine.compute_weighted_score(signals)
    # Expected: 15*0.35 + 90*0.30 = 5.25 + 27.0 = 32.25
    assert pytest.approx(weighted, 0.5) == 32.25
    final, boost = RiskScoringEngine.apply_cross_signal_boost(signals, weighted, delta_minutes=None)
    assert boost == 0.0  # tx anomaly < 60 so no boost


# ------------------------------------------------------------------------------
# 10. Combined Transaction + Communication Risk (Scenario D)
# ------------------------------------------------------------------------------
def test_10_combined_transaction_and_communication_risk():
    signals = RiskSignals(
        transaction_anomaly_score=70.0,
        communication_risk_score=75.0,
        behavioral_deviation_score=75.0,
        new_payee_score=100.0,
        velocity_score=70.0,
        temporal_correlation_score=40.0,
    )
    weighted = RiskScoringEngine.compute_weighted_score(signals)
    # 70*0.35 + 75*0.30 + 75*0.15 + 100*0.08 + 70*0.07 + 40*0.05
    # = 24.5 + 22.5 + 11.25 + 8.0 + 4.9 + 2.0 = 73.15
    assert pytest.approx(weighted, 0.5) == 73.15

    # With correlation within window, boost is +10
    final, boost = RiskScoringEngine.apply_cross_signal_boost(signals, weighted, delta_minutes=45.0)
    assert boost == 10.0
    assert pytest.approx(final, 0.5) == 83.15
    assert RiskFusionConfig.determine_risk_level(final) == "HIGH"


# ------------------------------------------------------------------------------
# 11. New Payee Signal
# ------------------------------------------------------------------------------
def test_11_new_payee_signal():
    sig_known = RiskSignals(transaction_anomaly_score=50.0, new_payee_score=0.0)
    sig_new = RiskSignals(transaction_anomaly_score=50.0, new_payee_score=100.0)
    diff = RiskScoringEngine.compute_weighted_score(sig_new) - RiskScoringEngine.compute_weighted_score(sig_known)
    assert pytest.approx(diff, 0.1) == 8.0  # 100 * 0.08 = 8 points


# ------------------------------------------------------------------------------
# 12. Velocity Signal
# ------------------------------------------------------------------------------
def test_12_velocity_signal():
    sig_base = RiskSignals(velocity_score=0.0)
    sig_fast = RiskSignals(velocity_score=100.0)
    diff = RiskScoringEngine.compute_weighted_score(sig_fast) - RiskScoringEngine.compute_weighted_score(sig_base)
    assert pytest.approx(diff, 0.1) == 7.0  # 100 * 0.07 = 7 points


# ------------------------------------------------------------------------------
# 13. Behavioral Deviation Signal
# ------------------------------------------------------------------------------
def test_13_behavioral_deviation_signal():
    sig_normal = RiskSignals(behavioral_deviation_score=0.0)
    sig_deviant = RiskSignals(behavioral_deviation_score=100.0)
    diff = RiskScoringEngine.compute_weighted_score(sig_deviant) - RiskScoringEngine.compute_weighted_score(sig_normal)
    assert pytest.approx(diff, 0.1) == 15.0  # 100 * 0.15 = 15 points


# ------------------------------------------------------------------------------
# 14. Temporal Correlation Within 2 Hours
# ------------------------------------------------------------------------------
def test_14_temporal_correlation_within_2_hours():
    now = datetime.now(timezone.utc)
    comm_time = now - timedelta(minutes=45)
    score, delta, within = TemporalCorrelationEngine.evaluate_candidate(
        tx_dt=now,
        comm_dt=comm_time,
        comm_risk=80.0,
        window_minutes=120,
    )
    assert within is True
    assert delta == 45.0
    # Proximity: 1.0 - (45 / 120) = 0.625. Score: 0.625 * 80 = 50.0
    assert pytest.approx(score, 0.1) == 50.0


# ------------------------------------------------------------------------------
# 15. Temporal Correlation Outside 2 Hours (Scenario F)
# ------------------------------------------------------------------------------
def test_15_temporal_correlation_outside_2_hours():
    now = datetime.now(timezone.utc)
    comm_time = now - timedelta(minutes=180)  # 3 hours ago
    score, delta, within = TemporalCorrelationEngine.evaluate_candidate(
        tx_dt=now,
        comm_dt=comm_time,
        comm_risk=95.0,
        window_minutes=120,
    )
    assert within is False
    assert delta == 180.0
    assert score == 0.0


# ------------------------------------------------------------------------------
# 16. Strong Temporal Correlation (Scenario E)
# ------------------------------------------------------------------------------
def test_16_strong_temporal_correlation():
    now = datetime.now(timezone.utc)
    comm_time = now - timedelta(minutes=10)  # 10 minutes ago
    score, delta, within = TemporalCorrelationEngine.evaluate_candidate(
        tx_dt=now,
        comm_dt=comm_time,
        comm_risk=90.0,
        window_minutes=120,
    )
    assert within is True
    # Proximity: 1 - 10/120 = 0.9167. Score: 0.9167 * 90 = 82.5
    assert pytest.approx(score, 0.5) == 82.5


# ------------------------------------------------------------------------------
# 17. No Communication Available
# ------------------------------------------------------------------------------
def test_17_no_communication_available():
    now = datetime.now(timezone.utc)
    match = TemporalCorrelationEngine.find_temporal_correlation(
        user_id="user_nonexistent",
        transaction_timestamp=now,
        candidate_communications=[],
    )
    assert match.within_window is False
    assert match.temporal_score == 0.0
    assert match.matched_communication_id is None


# ------------------------------------------------------------------------------
# 18. Normal Communication Ignored (Scenario G)
# ------------------------------------------------------------------------------
def test_18_normal_communication_ignored():
    now = datetime.now(timezone.utc)
    normal_candidates = [
        {
            "id": "msg_safe_01",
            "classification": "NORMAL",
            "risk_level": "LOW",
            "scam_probability": 5.0,
            "analyzed_at": (now - timedelta(minutes=15)).isoformat(),
        }
    ]
    match = TemporalCorrelationEngine.find_temporal_correlation(
        user_id="user_demo",
        transaction_timestamp=now,
        candidate_communications=normal_candidates,
    )
    # Must be ignored
    assert match.within_window is False
    assert match.temporal_score == 0.0


# ------------------------------------------------------------------------------
# 19. Correlation Boost Applied
# ------------------------------------------------------------------------------
def test_19_correlation_boost_applied():
    signals = RiskSignals(
        transaction_anomaly_score=65.0,
        communication_risk_score=70.0,
    )
    # Qualifies: comm >= 60, tx >= 60, delta = 30 <= 120
    final, boost = RiskScoringEngine.apply_cross_signal_boost(signals, 50.0, delta_minutes=30.0)
    assert boost == 10.0
    assert final == 60.0


# ------------------------------------------------------------------------------
# 20. Maximum Score Remains 100
# ------------------------------------------------------------------------------
def test_20_maximum_score_clamped_to_100():
    signals = RiskSignals(
        transaction_anomaly_score=95.0,
        communication_risk_score=95.0,
        behavioral_deviation_score=95.0,
        new_payee_score=100.0,
        velocity_score=95.0,
        temporal_correlation_score=95.0,
    )
    weighted = RiskScoringEngine.compute_weighted_score(signals)  # ~ 95.4
    final, boost = RiskScoringEngine.apply_cross_signal_boost(signals, weighted, delta_minutes=10.0)
    assert boost == 10.0
    assert final == 100.0  # Clamped strictly to 100.0


# ------------------------------------------------------------------------------
# 21. Explainability Output
# ------------------------------------------------------------------------------
def test_21_explainability():
    signals = RiskSignals(
        transaction_anomaly_score=85.0,
        communication_risk_score=90.0,
        temporal_correlation_score=80.0,
    )
    explanation_packet = RiskFusionExplainer.explain(
        signals=signals,
        risk_level="CRITICAL",
        correlation_boost=10.0,
    )
    assert "explanation" in explanation_packet
    assert "top_contributing_factors" in explanation_packet
    assert "recommended_action" in explanation_packet
    # Safety constraint: never say "Fraud confirmed"
    assert "fraud confirmed" not in explanation_packet["explanation"].lower()


# ------------------------------------------------------------------------------
# 22. Top Contributing Factors
# ------------------------------------------------------------------------------
def test_22_top_contributing_factors():
    signals = RiskSignals(
        transaction_anomaly_score=80.0,
        communication_risk_score=85.0,
        behavioral_deviation_score=70.0,
        new_payee_score=100.0,
        temporal_correlation_score=75.0,
    )
    factors = RiskFusionExplainer.get_top_contributing_factors(
        signals=signals,
        correlation_boost=10.0,
        unusual_time=True,
    )
    assert isinstance(factors, list)
    assert len(factors) >= 3
    assert any("shortly after suspicious communication" in f for f in factors)
    assert any("Suspicious communication" in f for f in factors)
    assert any("New or unfamiliar payee" in f for f in factors)


# ------------------------------------------------------------------------------
# 23. Recommended Action
# ------------------------------------------------------------------------------
def test_23_recommended_action():
    assert RiskFusionConfig.get_action_for_level("LOW") == RiskFusionConfig.ACTION_LOW
    assert RiskFusionConfig.get_action_for_level("MEDIUM") == RiskFusionConfig.ACTION_MEDIUM
    assert RiskFusionConfig.get_action_for_level("HIGH") == RiskFusionConfig.ACTION_HIGH
    assert RiskFusionConfig.get_action_for_level("CRITICAL") == RiskFusionConfig.ACTION_CRITICAL


# ------------------------------------------------------------------------------
# 24. Risk Event Persistence
# ------------------------------------------------------------------------------
def test_24_risk_event_persistence(app):
    with app.app_context():
        repo = RiskEventRepository()
        event = {
            "transaction_id": "TXN_PERSIST_TEST",
            "user_id": "usr_test",
            "final_risk_score": 88.0,
            "risk_level": "CRITICAL",
            "top_contributing_factors": ["Suspicious communication detected"],
            "explanation": "High-risk activity detected.",
        }
        saved = repo.save_risk_event(event)
        assert saved["id"] is not None
        fetched = repo.get_by_transaction_id("TXN_PERSIST_TEST")
        assert fetched is not None
        assert fetched["final_risk_score"] == 88.0


# ------------------------------------------------------------------------------
# 25. Alert Creation on High/Critical
# ------------------------------------------------------------------------------
def test_25_alert_creation_on_high_critical(app):
    with app.app_context():
        alert_repo = AlertRepository()
        service = RiskFusionService(alert_repo=alert_repo)
        now = datetime.now(timezone.utc)

        # High-risk transaction payload
        high_risk_tx = {
            "transaction_id": "TXN_ALERT_TEST_01",
            "user_id": "usr_alert_test",
            "amount": 48000.0,
            "payee": "Cyber Scammer Electric Board",
            "upiId": "scam.elec@okaxis",
            "is_new_payee": True,
            "timestamp": now.isoformat(),
        }
        recent_comm = [
            {
                "id": "msg_scam_01",
                "classification": "SCAM",
                "risk_level": "CRITICAL",
                "scam_probability": 95.0,
                "analyzed_at": (now - timedelta(minutes=15)).isoformat(),
            }
        ]

        result = service.analyze_transaction_risk(
            transaction_data=high_risk_tx,
            candidate_communications=recent_comm,
            create_alert_if_needed=True,
        )

        assert result["risk_level"] in ("HIGH", "CRITICAL")
        assert result["alert_created"] is True

        alert = alert_repo.get_by_transaction_id("TXN_ALERT_TEST_01")
        assert alert is not None
        assert alert["alert_type"] in ("RISK_FUSION_HIGH", "RISK_FUSION_CRITICAL")


# ------------------------------------------------------------------------------
# 26. Alert Deduplication
# ------------------------------------------------------------------------------
def test_26_alert_deduplication(app):
    with app.app_context():
        alert_repo = AlertRepository()
        service = RiskFusionService(alert_repo=alert_repo)
        now = datetime.now(timezone.utc)

        tx = {
            "transaction_id": "TXN_DEDUP_TEST",
            "user_id": "usr_dedup_test",
            "amount": 49000.0,
            "payee": "Fake Customs Officer",
            "upiId": "customs@upi",
            "is_new_payee": True,
            "timestamp": now.isoformat(),
        }
        recent_comm = [
            {
                "id": "msg_dedup_01",
                "classification": "SCAM",
                "risk_level": "CRITICAL",
                "scam_probability": 92.0,
                "analyzed_at": (now - timedelta(minutes=20)).isoformat(),
            }
        ]

        # First run -> alert created
        res1 = service.analyze_transaction_risk(tx, candidate_communications=recent_comm)
        assert res1["alert_created"] is True

        # Second run -> alert NOT duplicated
        res2 = service.analyze_transaction_risk(tx, candidate_communications=recent_comm)
        assert res2["alert_created"] is False


# ------------------------------------------------------------------------------
# 27. API Request Validation
# ------------------------------------------------------------------------------
def test_27_api_request_validation(client):
    # Invalid body
    resp = client.post("/api/risk/analyze", json="invalid-string")
    assert resp.status_code == 400

    # Negative amount
    resp = client.post("/api/risk/analyze", json={"payee": "Merchant", "amount": -50, "upiId": "m@upi"})
    assert resp.status_code == 400

    # Missing payee
    resp = client.post("/api/risk/analyze", json={"amount": 500, "upiId": "m@upi"})
    assert resp.status_code == 400


# ------------------------------------------------------------------------------
# 28. API Response Schema
# ------------------------------------------------------------------------------
def test_28_api_response_schema(client):
    payload = {
        "payee": "Pharmacy Store",
        "amount": 450.0,
        "upiId": "pharma@okaxis",
        "user_id": "usr_sunita_68",
    }
    resp = client.post("/api/risk/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "analysis" in data
    anl = data["analysis"]
    required_fields = [
        "transaction_id",
        "user_id",
        "transaction_anomaly_score",
        "communication_risk_score",
        "behavioral_deviation_score",
        "new_payee_score",
        "velocity_score",
        "temporal_correlation_score",
        "correlation_boost",
        "final_risk_score",
        "risk_level",
        "top_contributing_factors",
        "explanation",
        "recommended_action",
        "alert_created",
    ]
    for rf in required_fields:
        assert rf in anl, f"Missing field '{rf}' in analysis response"


# ------------------------------------------------------------------------------
# 29. Missing Transaction Handling
# ------------------------------------------------------------------------------
def test_29_missing_transaction_handling(client):
    resp = client.post("/api/risk/analyze", json={"transaction_id": "TXN_DOES_NOT_EXIST_999"})
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data


# ------------------------------------------------------------------------------
# 30. Missing Communication Handling
# ------------------------------------------------------------------------------
def test_30_missing_communication_handling(client):
    # Valid normal transaction for user who has no prior communications
    payload = {
        "user_id": "usr_brand_new_no_sms",
        "payee": "Sharma General Store",
        "amount": 2500.0,
        "upiId": "sharma@okaxis",
        "is_new_payee": False,
    }
    resp = client.post("/api/risk/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    anl = data["analysis"]
    assert anl["communication_risk_score"] == 0.0
    assert anl["temporal_correlation_score"] == 0.0
    assert anl["correlation_boost"] == 0.0
    assert anl["risk_level"] == "LOW"


# ------------------------------------------------------------------------------
# 31. Phase 4 Isolation Forest Regression Test
# ------------------------------------------------------------------------------
def test_31_phase_4_ml_regression(client):
    payload = {
        "payee": "Known Milk Dairy",
        "amount": 120.0,
        "upiId": "milk@upi",
    }
    resp = client.post("/api/analyze-transaction", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "analysis" in data
    assert "anomaly_score" in data["analysis"]


# ------------------------------------------------------------------------------
# 32. Phase 5 NLP Scam Detection Regression Test
# ------------------------------------------------------------------------------
def test_32_phase_5_nlp_regression(client):
    payload = {
        "text": "Your electricity connection will be disconnected tonight at 9:30 PM. Call immediately.",
        "message_type": "sms",
    }
    resp = client.post("/api/analyze-message", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "analysis" in data
    assert data["analysis"]["classification"] in ("SUSPICIOUS", "SCAM")
