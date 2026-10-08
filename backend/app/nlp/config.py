"""UPI Guardian - NLP Scam Communication Analyzer Configuration.

Defines classes, categories, model hyperparameters, risk boundaries,
and artifact file paths for SMS and call transcript scam detection.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "models" / "artifacts"
DEFAULT_VECTORIZER_FILENAME = "tfidf_vectorizer.joblib"
DEFAULT_CLASSIFIER_FILENAME = "scam_classifier.joblib"
DEFAULT_METADATA_FILENAME = "metadata.json"

DEFAULT_VECTORIZER_PATH = ARTIFACTS_DIR / DEFAULT_VECTORIZER_FILENAME
DEFAULT_CLASSIFIER_PATH = ARTIFACTS_DIR / DEFAULT_CLASSIFIER_FILENAME
DEFAULT_METADATA_PATH = ARTIFACTS_DIR / DEFAULT_METADATA_FILENAME

# Classes
CLASS_NAMES: list[str] = ["NORMAL", "SUSPICIOUS", "SCAM"]

# 14 Supported Scam / Coercion Categories
SCAM_CATEGORIES: list[str] = [
    "OTP_REQUEST",
    "UPI_PIN_REQUEST",
    "KYC_THREAT",
    "ACCOUNT_BLOCK_THREAT",
    "URGENT_PAYMENT",
    "FAKE_BANK_SUPPORT",
    "FAKE_UPI_SUPPORT",
    "PRIZE_REWARD_SCAM",
    "IMPERSONATION",
    "REMOTE_ACCESS_REQUEST",
    "SUSPICIOUS_PAYMENT_LINK",
    "ELECTRICITY_DISCONNECTION_SCAM",
    "LOAN_OR_REFUND_SCAM",
    "DELIVERY_OR_CUSTOMS_SCAM",
]

# Supported Message Types
ALLOWED_MESSAGE_TYPES: set[str] = {"sms", "call_transcript", "call"}

# Hyperparameters & Model Configuration
MODEL_VERSION: str = "1.0.0"
MODEL_NAME: str = "TFIDF_LogisticRegression_ScamClassifier"
RANDOM_SEED: int = 42

# TF-IDF Configuration
TFIDF_MAX_FEATURES: int = 2500
TFIDF_NGRAM_RANGE: tuple[int, int] = (1, 2)
TFIDF_SUBLINEAR_TF: bool = True
TFIDF_MIN_DF: int = 1

# Logistic Regression Configuration
LOGREG_MAX_ITER: int = 1000
LOGREG_C: float = 2.0
LOGREG_CLASS_WEIGHT: str = "balanced"

# NLP Risk Level Thresholds (0 - 100 scale based on scam probability)
# 0 to 24: LOW (safe)
# 25 to 49: MEDIUM (review)
# 50 to 74: HIGH (high)
# 75 to 100: CRITICAL (critical)
RISK_LOW_MAX: float = 24.0
RISK_MEDIUM_MAX: float = 49.0
RISK_HIGH_MAX: float = 74.0

# Alert creation threshold
ALERT_TRIGGER_SCORE: float = 50.0
