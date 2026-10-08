"""UPI Guardian - Isolation Forest Anomaly Detection Model.

Encapsulates training, serialization, loading, and inference of scikit-learn's Isolation Forest.

Key design principles:
- Training is strictly separated from inference (API never retrains during request handling).
- Artifacts are serialized via joblib with complete reproducible metadata.
- Model artifact is loaded once into a thread-safe singleton cache.
- Explicit errors are raised if model artifact is missing (no silent fake ML fallbacks).
- Scores are normalized to 0-100 where higher indicates greater behavioral anomaly.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import threading
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from app.ml.config import (
    CONTAMINATION,
    DEFAULT_METADATA_PATH,
    DEFAULT_MODEL_PATH,
    FEATURE_NAMES,
    MODEL_NAME,
    MODEL_VERSION,
    N_ESTIMATORS,
    RANDOM_STATE,
    SCORE_HIGH_MAX,
    SCORE_LOW_MAX,
    SCORE_MEDIUM_MAX,
)


class ModelNotTrainedError(Exception):
    """Raised when an inference request is made but no trained model artifact exists."""


class IsolationForestModel:
    """Manages training, persistence, and inference for the Isolation Forest detector."""

    _cached_model = None
    _cached_metadata = None
    _lock = threading.Lock()

    def __init__(
        self,
        n_estimators: int = N_ESTIMATORS,
        contamination: float = CONTAMINATION,
        random_state: int = RANDOM_STATE,
        model_version: str = MODEL_VERSION,
    ):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.model_version = model_version
        self.estimator = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            bootstrap=False,
            n_jobs=-1,
        )

    def train(self, X: np.ndarray | list[list[float]]) -> dict:
        """Train the Isolation Forest on a 2D feature matrix.

        Args:
            X: 2D array of shape (n_samples, 5) matching FEATURE_NAMES.

        Returns:
            dict containing training summary metrics.
        """
        X_arr = np.asarray(X, dtype=np.float64)
        if X_arr.ndim != 2 or X_arr.shape[1] != len(FEATURE_NAMES):
            raise ValueError(
                f"Expected 2D array with {len(FEATURE_NAMES)} features ({FEATURE_NAMES}), got shape {X_arr.shape}"
            )

        # Ensure no NaN or Inf
        X_arr = np.nan_to_num(X_arr, nan=0.0, posinf=9999.0, neginf=-9999.0)

        # Fit model
        self.estimator.fit(X_arr)

        # Evaluate baseline distribution
        decisions = self.estimator.decision_function(X_arr)
        preds = self.estimator.predict(X_arr)  # -1 = anomaly, 1 = normal

        detected_anomalies = int((preds == -1).sum())
        total_samples = len(X_arr)

        summary = {
            "model_type": MODEL_NAME,
            "version": self.model_version,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "n_samples": total_samples,
            "n_features": len(FEATURE_NAMES),
            "feature_names": FEATURE_NAMES,
            "contamination": self.contamination,
            "n_estimators": self.n_estimators,
            "random_state": self.random_state,
            "anomalies_detected_in_train": detected_anomalies,
            "anomaly_rate": round(detected_anomalies / total_samples, 4) if total_samples else 0.0,
            "decision_min": round(float(np.min(decisions)), 4),
            "decision_max": round(float(np.max(decisions)), 4),
            "decision_mean": round(float(np.mean(decisions)), 4),
        }
        return summary

    def save(
        self,
        model_path: Path | str = DEFAULT_MODEL_PATH,
        metadata_path: Path | str = DEFAULT_METADATA_PATH,
        extra_metadata: dict | None = None,
    ) -> None:
        """Serialize trained model and write metadata JSON."""
        model_p = Path(model_path)
        meta_p = Path(metadata_path)

        # Ensure parent directories exist
        model_p.parent.mkdir(parents=True, exist_ok=True)
        meta_p.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.estimator, model_p)

        meta = {
            "model_name": MODEL_NAME,
            "model_version": self.model_version,
            "n_estimators": self.n_estimators,
            "contamination": self.contamination,
            "random_state": self.random_state,
            "features": FEATURE_NAMES,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        if extra_metadata:
            meta.update(extra_metadata)

        with open(meta_p, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        # Update cache
        with self._lock:
            IsolationForestModel._cached_model = self.estimator
            IsolationForestModel._cached_metadata = meta

    @classmethod
    def load(
        cls,
        model_path: Path | str = DEFAULT_MODEL_PATH,
        metadata_path: Path | str = DEFAULT_METADATA_PATH,
        force_reload: bool = False,
    ) -> tuple[IsolationForest, dict]:
        """Load trained model and metadata from disk using thread-safe singleton cache.

        Raises:
            ModelNotTrainedError: If model artifact does not exist on disk.
        """
        model_p = Path(model_path)
        meta_p = Path(metadata_path)

        with cls._lock:
            if not force_reload and cls._cached_model is not None and cls._cached_metadata is not None:
                return cls._cached_model, cls._cached_metadata

            if not model_p.exists():
                raise ModelNotTrainedError(
                    f"Model artifact not found at '{model_p}'. Run 'python scripts/train_anomaly_model.py' to generate model artifacts."
                )

            model = joblib.load(model_p)
            metadata = {}
            if meta_p.exists():
                try:
                    with open(meta_p, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                except Exception:
                    metadata = {"model_name": MODEL_NAME, "model_version": MODEL_VERSION}

            cls._cached_model = model
            cls._cached_metadata = metadata
            return model, metadata

    @classmethod
    def clear_cache(cls) -> None:
        """Clear singleton model cache (useful for testing)."""
        with cls._lock:
            cls._cached_model = None
            cls._cached_metadata = None

    @classmethod
    def compute_anomaly_score(cls, raw_decision: float) -> float:
        """Convert Isolation Forest decision_function value to a 0-100 anomaly score.

        In scikit-learn IsolationForest:
        - raw_decision < 0 indicates anomaly (predict == -1)
        - raw_decision >= 0 indicates normal inlier (predict == 1)
        - typical raw_decision ranges from approx -0.20 to +0.25

        Calibrated Piecewise Mapping:
        - raw_decision = 0.0 -> score = 50.0 (decision boundary)
        - When raw_decision < 0 (anomalous): maps [0.0, -0.20] -> [50.0, 100.0] with slope 260.0
          raw_decision = -0.10 -> 50.0 + 26.0 = 76.0 (HIGH)
          raw_decision = -0.15 -> 50.0 + 39.0 = 89.0 (CRITICAL)
        - When raw_decision >= 0 (normal): maps [0.0, +0.25] -> [50.0, 0.0] with slope 200.0
          raw_decision = +0.10 -> 50.0 - 20.0 = 30.0 (LOW)
          raw_decision = +0.20 -> 50.0 - 40.0 = 10.0 (LOW)
        """
        d = float(raw_decision)
        if d < 0:
            score = 50.0 + (-d * 260.0)
        else:
            score = 50.0 - (d * 200.0)
        clamped = max(0.0, min(100.0, score))
        return round(clamped, 1)

    @classmethod
    def determine_risk_level(cls, anomaly_score: float) -> str:
        """Map normalized 0-100 anomaly score to risk level.

        Returns one of: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'.
        """
        if anomaly_score <= SCORE_LOW_MAX:
            return "LOW"
        if anomaly_score <= SCORE_MEDIUM_MAX:
            return "MEDIUM"
        if anomaly_score <= SCORE_HIGH_MAX:
            return "HIGH"
        return "CRITICAL"
