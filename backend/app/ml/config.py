"""UPI Guardian - Machine Learning Configuration.

Defines feature names, model hyperparameters, scoring thresholds,
and artifact file paths for the Isolation Forest transaction anomaly detection engine.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "models" / "artifacts"
DEFAULT_MODEL_FILENAME = "isolation_forest_v1.joblib"
DEFAULT_METADATA_FILENAME = "metadata.json"
DEFAULT_MODEL_PATH = ARTIFACTS_DIR / DEFAULT_MODEL_FILENAME
DEFAULT_METADATA_PATH = ARTIFACTS_DIR / DEFAULT_METADATA_FILENAME

# Feature definitions
FEATURE_NAMES: list[str] = [
    "amount",
    "z_score_deviation",
    "velocity",
    "is_new_payee",
    "unusual_time",
]

# Model Hyperparameters
N_ESTIMATORS: int = 150
CONTAMINATION: float = 0.08
RANDOM_STATE: int = 42
MODEL_VERSION: str = "1.0.0"
MODEL_NAME: str = "IsolationForest"

# Anomaly Scoring & Risk Thresholds (0 - 100 Scale)
# 0 to 30: LOW
# 31 to 60: MEDIUM
# 61 to 85: HIGH
# 86 to 100: CRITICAL
SCORE_LOW_MAX: float = 30.0
SCORE_MEDIUM_MAX: float = 60.0
SCORE_HIGH_MAX: float = 85.0

# Alert trigger threshold (anomaly score >= 60 triggers alert)
ALERT_TRIGGER_SCORE: float = 60.0

# Time boundaries (24-hour format)
# Unusual transaction hours for elderly demographic: 23:00 to 05:00 (11 PM to 5 AM)
UNUSUAL_HOURS: set[int] = {23, 0, 1, 2, 3, 4}
