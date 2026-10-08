"""UPI Guardian - Comprehensive NLP Test Suite.

Covers all 33 Phase 5 validation requirements:
1. text preprocessing
2. empty text validation
3. null text validation
4. TF-IDF training
5. TF-IDF serialization/loading
6. classifier training
7. classifier serialization/loading
8. inference
9. probability range
10. NORMAL message
11. SUSPICIOUS message
12. OTP scam
13. UPI PIN scam
14. KYC scam
15. account-block scam
16. fake support scam
17. reward scam
18. remote access scam
19. suspicious link
20. electricity disconnection scam
21. impersonation scam
22. call transcript
23. category detection
24. suspicious phrase extraction
25. risk level calculation
26. recommended action
27. missing model handling
28. invalid message type
29. MongoDB persistence
30. duplicate analysis prevention
31. alert creation
32. duplicate alert prevention
33. POST /api/analyze-message integration
"""

from pathlib import Path
import tempfile
import pytest

from app.db.repositories.alert_repository import AlertRepository
from app.db.repositories.message_repository import MessageRepository
from app.nlp.data.dataset import ScamDatasetGenerator
from app.nlp.explainability.explainer import ScamExplainer
from app.nlp.features.tfidf import TfidfFeatureExtractor
from app.nlp.inference.service import NLPScamDetectionService
from app.nlp.models.scam_classifier import NLPModelNotTrainedError, ScamClassifier
from app.nlp.preprocessing.text_cleaner import TextCleaner
from app.schemas.validators import validate_analyze_message
from app.utils.errors import ValidationError


# =====================================================================
# 1-3. PREPROCESSING & TEXT SAFETY
# =====================================================================

def test_1_text_preprocessing():
    """Verify text cleaner lowercases, cleans punctuation, and normalizes URLs and numbers."""
    raw = "URGENT! Click https://scam-bank.biz/pay or call +91 98201 12345 to verify your account!!!"
    cleaned = TextCleaner.clean(raw)
    assert "urgent" in cleaned
    assert "link_url" in cleaned
    assert "phone_num" in cleaned
    assert "!" not in cleaned
    assert TextCleaner.compute_hash(raw) == TextCleaner.compute_hash(raw)


def test_2_empty_text_validation():
    """Verify empty or blank text is handled safely by cleaner and rejected by validator."""
    assert TextCleaner.clean("") == ""
    assert TextCleaner.clean("   ") == ""
    with pytest.raises(ValidationError):
        validate_analyze_message({"text": "", "message_type": "sms"})
    with pytest.raises(ValidationError):
        validate_analyze_message({"text": "   ", "message_type": "sms"})


def test_3_null_text_validation():
    """Verify None text is handled safely by cleaner and rejected by validator."""
    assert TextCleaner.clean(None) == ""
    with pytest.raises(ValidationError):
        validate_analyze_message({"text": None, "message_type": "sms"})
    with pytest.raises(ValidationError):
        validate_analyze_message({"message_type": "sms"})


# =====================================================================
# 4-7. TF-IDF & CLASSIFIER TRAINING / SERIALIZATION
# =====================================================================

def test_4_tfidf_training():
    """Verify TF-IDF vectorizer fits on text corpus and produces non-empty vocabulary."""
    texts = [
        "your account is blocked",
        "routine bill payment received",
        "share your otp to verify",
    ]
    extractor = TfidfFeatureExtractor()
    matrix = extractor.fit_transform(texts)
    assert matrix.shape[0] == 3
    assert matrix.shape[1] > 0
    assert extractor.is_fitted is True


def test_5_tfidf_serialization_loading():
    """Verify TF-IDF vectorizer can be saved and reloaded using joblib."""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "test_tfidf.joblib"
        extractor = TfidfFeatureExtractor()
        extractor.fit(["sbi fraud department", "electricity bill payment"])
        extractor.save(save_path)

        assert save_path.exists()
        loaded = TfidfFeatureExtractor.load(save_path)
        assert loaded.is_fitted is True
        vec = loaded.transform("sbi fraud department")
        assert vec.shape[1] == loaded.vectorizer.max_features or vec.nnz > 0


def test_6_classifier_training():
    """Verify LogisticRegression fits on TF-IDF features and predicts classes."""
    corpus = [
        "your pension was credited to your account XX4109",
        "your account will be blocked share otp immediately",
        "special cashback reward pending check link",
    ]
    labels = ["NORMAL", "SCAM", "SUSPICIOUS"]
    extractor = TfidfFeatureExtractor()
    X = extractor.fit_transform(corpus)

    clf = ScamClassifier()
    summary = clf.train(X, labels)
    assert set(summary["classes"]) == {"NORMAL", "SCAM", "SUSPICIOUS"}


def test_7_classifier_serialization_loading():
    """Verify classifier can be saved to disk and loaded without loss of accuracy."""
    with tempfile.TemporaryDirectory() as tmpdir:
        clf_path = Path(tmpdir) / "test_clf.joblib"
        meta_path = Path(tmpdir) / "test_meta.json"

        extractor = TfidfFeatureExtractor()
        X = extractor.fit_transform(["normal banking message", "scam threat share otp"])
        y = ["NORMAL", "SCAM"]

        clf = ScamClassifier()
        clf.train(X, y)
        clf.save(classifier_path=clf_path, metadata_path=meta_path)

        assert clf_path.exists()
        assert meta_path.exists()

        ScamClassifier.clear_cache()
        loaded_clf, loaded_meta = ScamClassifier.load(clf_path, meta_path, force_reload=True)
        assert loaded_meta["model_name"] == "TFIDF_LogisticRegression_ScamClassifier"
        pred = loaded_clf.predict(extractor.transform(["scam threat share otp"]))[0]
        assert pred == "SCAM"
        ScamClassifier.clear_cache()


# =====================================================================
# 8-11. INFERENCE, PROBABILITIES & BASIC CLASSIFICATION
# =====================================================================

def test_8_inference():
    """Verify inference pipeline processes a candidate communication text."""
    service = NLPScamDetectionService()
    res = service.analyze("Your electricity bill payment of Rs 1,840 was received successfully.", "sms")
    assert "classification" in res
    assert "scam_probability" in res
    assert "risk_level" in res
    assert "categories" in res
    assert "explanation" in res
    assert "recommended_action" in res


def test_9_probability_range():
    """Verify probability estimate is always within [0.0, 100.0]."""
    probs1 = {"NORMAL": 0.99, "SUSPICIOUS": 0.01, "SCAM": 0.00}
    probs2 = {"NORMAL": 0.05, "SUSPICIOUS": 0.45, "SCAM": 0.50}
    probs3 = {"NORMAL": 0.00, "SUSPICIOUS": 0.05, "SCAM": 0.95}

    s1 = ScamClassifier.compute_scam_probability(probs1)
    s2 = ScamClassifier.compute_scam_probability(probs2)
    s3 = ScamClassifier.compute_scam_probability(probs3)

    assert 0.0 <= s1 <= 100.0
    assert 0.0 <= s2 <= 100.0
    assert 0.0 <= s3 <= 100.0
    assert s1 < s2 < s3


def test_10_normal_message():
    """Verify benign messages are classified as NORMAL with LOW risk."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "Your A/c XX4109 is debited by Rs 1,250.00 on 28-Sep-26 at FRESH BASKET. Available balance: Rs 42,310.00.",
        "sms",
    )
    assert res["classification"] == "NORMAL"
    assert res["risk_level"] == "LOW"
    assert res["scam_probability"] < 25.0


def test_11_suspicious_message():
    """Verify promotional / unsolicited warning messages are classified as SUSPICIOUS."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "Dear user, you have unredeemed rewards points worth Rs 4,500. Check points at reward-points-portal.net",
        "sms",
    )
    assert res["classification"] in ("SUSPICIOUS", "SCAM")
    assert res["scam_probability"] >= 20.0


# =====================================================================
# 12-21. THE 14 SCAM CATEGORY DETECTIONS
# =====================================================================

def test_12_otp_scam():
    """Verify OTP extortion triggers OTP_REQUEST category and SCAM classification."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "URGENT: Your SBI account has been compromised. Send OTP immediately to verify reversal.",
        "sms",
    )
    assert res["classification"] == "SCAM"
    assert "OTP_REQUEST" in res["categories"]


def test_13_upi_pin_scam():
    """Verify UPI PIN request triggers UPI_PIN_REQUEST category."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "Refund of Rs 8,500 waiting for your account. Enter UPI PIN on payment screen to accept credit.",
        "sms",
    )
    assert res["classification"] == "SCAM"
    assert "UPI_PIN_REQUEST" in res["categories"]


def test_14_kyc_scam():
    """Verify KYC suspension threat triggers KYC_THREAT category."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "IMPORTANT NOTICE: Your SBI KYC has expired today. Your bank account will be permanently blocked within 24 hours. Update KYC immediately.",
        "sms",
    )
    assert res["classification"] == "SCAM"
    assert "KYC_THREAT" in res["categories"]


def test_15_account_block_scam():
    """Verify account freeze threat triggers ACCOUNT_BLOCK_THREAT."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "FINAL WARNING: Your HDFC bank account will be blocked today due to suspicious activity. Unfreeze immediately.",
        "sms",
    )
    assert res["classification"] == "SCAM"
    assert "ACCOUNT_BLOCK_THREAT" in res["categories"]


def test_16_fake_support_scam():
    """Verify fake bank support claim triggers FAKE_BANK_SUPPORT."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "Calling from bank fraud department. Your account is being hacked right now. Contact helpline officer immediately.",
        "call_transcript",
    )
    assert res["classification"] == "SCAM"
    assert "FAKE_BANK_SUPPORT" in res["categories"]


def test_17_reward_scam():
    """Verify lottery / prize claim triggers PRIZE_REWARD_SCAM."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "CONGRATULATIONS! Your mobile number won Rs 25,00,000 in KBC Jio Lucky Draw 2026. Claim prize now.",
        "sms",
    )
    assert res["classification"] == "SCAM"
    assert "PRIZE_REWARD_SCAM" in res["categories"]


def test_18_remote_access_scam():
    """Verify AnyDesk / TeamViewer request triggers REMOTE_ACCESS_REQUEST."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "To fix your mobile banking error, install AnyDesk application from playstore and tell the 9-digit code.",
        "sms",
    )
    assert res["classification"] == "SCAM"
    assert "REMOTE_ACCESS_REQUEST" in res["categories"]


def test_19_suspicious_link():
    """Verify suspicious link triggers SUSPICIOUS_PAYMENT_LINK."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "Alert: Pay immediately at bit.ly/secure-pay to prevent card deactivation.",
        "sms",
    )
    assert "SUSPICIOUS_PAYMENT_LINK" in res["categories"]


def test_20_electricity_disconnection_scam():
    """Verify electricity cut scam triggers ELECTRICITY_DISCONNECTION_SCAM."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "Dear Consumer, Your Electricity power will be disconnected Tonight at 9.30 PM from electricity office because previous month bill was not updated.",
        "sms",
    )
    assert res["classification"] == "SCAM"
    assert "ELECTRICITY_DISCONNECTION_SCAM" in res["categories"]


def test_21_impersonation_scam():
    """Verify impersonation of police or authority is detected."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "I am calling from police headquarters. Your son Rajesh is in emergency police custody. Send money on UPI.",
        "call_transcript",
    )
    assert res["classification"] == "SCAM"
    assert "IMPERSONATION" in res["categories"]


# =====================================================================
# 22-26. FORMATS, PHRASES, RISK & ACTIONS
# =====================================================================

def test_22_call_transcript():
    """Verify call transcript format is analyzed properly."""
    service = NLPScamDetectionService()
    res = service.analyze(
        "Caller: Hello Sunita ji, this is Dr. Mehta's assistant calling to confirm your routine checkup tomorrow at 11:00 AM.",
        "call_transcript",
    )
    assert res["message_type"] == "call_transcript"
    assert res["classification"] == "NORMAL"


def test_23_category_detection():
    """Verify multiple matching categories can be detected simultaneously."""
    text = "Your account will be blocked today. Send OTP immediately to avoid disconnection."
    exp = ScamExplainer.explain(text, "SCAM", 95.0, "CRITICAL")
    cats = exp["categories"]
    assert "ACCOUNT_BLOCK_THREAT" in cats
    assert "OTP_REQUEST" in cats


def test_24_suspicious_phrase_extraction():
    """Verify matched key phrases are extracted for transparency."""
    text = "Dear customer, your SBI KYC has expired today. Account will be blocked."
    exp = ScamExplainer.explain(text, "SCAM", 90.0, "HIGH")
    assert len(exp["suspicious_phrases"]) > 0


def test_25_risk_level_calculation():
    """Verify risk levels correctly map according to documented thresholds."""
    assert ScamClassifier.determine_risk_level(15.0, "NORMAL") == "LOW"
    assert ScamClassifier.determine_risk_level(35.0, "SUSPICIOUS") == "MEDIUM"
    assert ScamClassifier.determine_risk_level(65.0, "SCAM") == "HIGH"
    assert ScamClassifier.determine_risk_level(90.0, "SCAM") == "CRITICAL"


def test_26_recommended_action():
    """Verify elder-friendly advice matches scam type."""
    exp_scam = ScamExplainer.explain("Send your OTP now", "SCAM", 95.0, "CRITICAL")
    assert "Do NOT share your OTP" in exp_scam["recommended_action"]

    exp_normal = ScamExplainer.explain("Bill receipt", "NORMAL", 10.0, "LOW")
    assert "Continue normally" in exp_normal["recommended_action"]


# =====================================================================
# 27-33. SAFETY, VALIDATION, DB, IDEMPOTENCY & ENDPOINT INTEGRATION
# =====================================================================

def test_27_missing_model_handling():
    """Verify clear error is raised if NLP artifacts are missing."""
    service = NLPScamDetectionService(
        classifier_path=Path("non_existent/clf.joblib"),
        vectorizer_path=Path("non_existent/vec.joblib"),
    )
    ScamClassifier.clear_cache()
    with pytest.raises(NLPModelNotTrainedError):
        service.analyze("test message")


def test_28_invalid_message_type(client):
    """Verify invalid message type is rejected with HTTP 400."""
    res = client.post("/api/analyze-message", json={"text": "hello test", "message_type": "telegram"})
    assert res.status_code == 400


def test_29_mongodb_persistence(client):
    """Verify analyzed message is saved in analyzed_messages collection."""
    repo = MessageRepository()
    initial_count = repo.collection.count_documents({})

    res = client.post(
        "/api/analyze-message",
        json={"text": "Your water bill payment of Rs 350 is successful.", "message_type": "sms"},
    )
    assert res.status_code == 200
    assert repo.collection.count_documents({}) >= initial_count + 1


def test_30_duplicate_analysis_prevention(client):
    """Verify submitting the identical message twice updates rather than duplicates."""
    payload = {
        "text": "Your account will be blocked today. Send OTP immediately.",
        "message_type": "sms",
        "user_id": "usr_test_idempotent",
    }
    res1 = client.post("/api/analyze-message", json=payload)
    assert res1.status_code == 200

    repo = MessageRepository()
    h = TextCleaner.compute_hash(payload["text"])
    docs1 = list(repo.collection.find({"user_id": "usr_test_idempotent", "text_hash": h}))
    assert len(docs1) == 1

    # Resubmit identical text
    res2 = client.post("/api/analyze-message", json=payload)
    assert res2.status_code == 200
    docs2 = list(repo.collection.find({"user_id": "usr_test_idempotent", "text_hash": h}))
    assert len(docs2) == 1  # No duplicate record created!


def test_31_alert_creation_on_scam(client):
    """Verify scam message creates a pending alert in alerts collection."""
    res = client.post(
        "/api/analyze-message",
        json={
            "text": "URGENT: Your SBI account has been compromised. Send OTP immediately to verify reversal.",
            "message_type": "sms",
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["alert"] is not None
    assert data["alert"]["alert_type"] == "SCAM_COMMUNICATION"
    assert data["alert"]["title"] == "Suspicious communication detected"
    assert data["alert"]["status"] == "pending"


def test_32_duplicate_alert_prevention(client):
    """Verify resubmitting the same scam message does not create a duplicate alert."""
    payload = {
        "text": "Electricity will be disconnected Tonight at 9.30 PM. Call 9820114920 immediately.",
        "message_type": "sms",
    }
    res1 = client.post("/api/analyze-message", json=payload)
    data1 = res1.get_json()
    alert1 = data1["alert"]
    assert alert1 is not None

    # Resubmit identical scam message
    res2 = client.post("/api/analyze-message", json=payload)
    data2 = res2.get_json()
    alert2 = data2["alert"]
    assert alert2 is not None
    assert alert1["id"] == alert2["id"]  # Identical alert returned!


def test_33_api_endpoint_integration(client):
    """Verify complete end-to-end integration via Flask REST API."""
    payload = {
        "user_id": "usr_sunita_68",
        "message_type": "call_transcript",
        "text": "Madam install AnyDesk application from playstore and give me 9 digit code.",
    }
    response = client.post("/api/analyze-message", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["analysis"]["classification"] == "SCAM"
    assert data["analysis"]["risk_level"] in ("HIGH", "CRITICAL")
    assert "REMOTE_ACCESS_REQUEST" in data["analysis"]["categories"]
    assert "Do NOT install AnyDesk" in data["analysis"]["recommended_action"]
