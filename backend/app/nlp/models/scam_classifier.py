"""UPI Guardian - NLP Scam Communication Classifier.

Implements multi-class LogisticRegression on TF-IDF features to classify
communications into NORMAL, SUSPICIOUS, or SCAM.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import threading
import joblib
import numpy as np
from scipy.sparse import spmatrix
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from app.nlp.config import (
    CLASS_NAMES,
    DEFAULT_CLASSIFIER_PATH,
    DEFAULT_METADATA_PATH,
    LOGREG_C,
    LOGREG_CLASS_WEIGHT,
    LOGREG_MAX_ITER,
    MODEL_NAME,
    MODEL_VERSION,
    RANDOM_SEED,
    RISK_HIGH_MAX,
    RISK_LOW_MAX,
    RISK_MEDIUM_MAX,
)


class NLPModelNotTrainedError(Exception):
    """Raised when an NLP inference request is received but trained artifacts do not exist."""


class ScamClassifier:
    """Manages training, metrics evaluation, persistence, and inference for the NLP scam classifier."""

    _cached_classifier = None
    _cached_metadata = None
    _lock = threading.Lock()

    def __init__(
        self,
        c_param: float = LOGREG_C,
        max_iter: int = LOGREG_MAX_ITER,
        class_weight: str | None = LOGREG_CLASS_WEIGHT,
        random_state: int = RANDOM_SEED,
    ):
        self.c_param = c_param
        self.max_iter = max_iter
        self.class_weight = class_weight
        self.random_state = random_state
        self.classifier = LogisticRegression(
            C=self.c_param,
            max_iter=self.max_iter,
            class_weight=self.class_weight,
            random_state=self.random_state,
        )
        self.classes_ = list(CLASS_NAMES)

    def train(self, X: spmatrix, y: list[str] | np.ndarray) -> dict:
        """Fit classifier on TF-IDF sparse matrix and target labels."""
        self.classifier.fit(X, y)
        self.classes_ = list(self.classifier.classes_)
        return {"classes": self.classes_, "n_samples": X.shape[0], "n_features": X.shape[1]}

    def evaluate(self, X_val: spmatrix, y_val: list[str] | np.ndarray) -> dict:
        """Compute performance metrics (accuracy, precision, recall, f1, confusion matrix)."""
        y_pred = self.classifier.predict(X_val)
        acc = float(accuracy_score(y_val, y_pred))
        report = classification_report(y_val, y_pred, output_dict=True, zero_division=0)
        conf_mat = confusion_matrix(y_val, y_pred, labels=self.classes_).tolist()

        return {
            "accuracy": round(acc, 4),
            "classification_report": report,
            "confusion_matrix": conf_mat,
            "classes": self.classes_,
        }

    def predict_probabilities(self, X: spmatrix) -> dict[str, float]:
        """Predict class probability distribution for a single sample."""
        probas = self.classifier.predict_proba(X)[0]
        result = {}
        for idx, cls_name in enumerate(self.classifier.classes_):
            result[cls_name] = round(float(probas[idx]), 4)
        return result

    @classmethod
    def compute_scam_probability(cls, class_probs: dict[str, float]) -> float:
        """Synthesize a normalized 0-100 scam risk probability estimate.

        Combines direct SCAM class probability with a weighted component from SUSPICIOUS probability.
        """
        p_scam = class_probs.get("SCAM", 0.0)
        p_susp = class_probs.get("SUSPICIOUS", 0.0)
        score = (p_scam * 100.0) + (p_susp * 45.0)
        return round(float(np.clip(score, 0.0, 100.0)), 1)

    @classmethod
    def determine_risk_level(cls, scam_probability: float, classification: str) -> str:
        """Map scam probability and predicted class to risk level."""
        if scam_probability <= RISK_LOW_MAX:
            return "LOW"
        if scam_probability <= RISK_MEDIUM_MAX:
            return "MEDIUM"
        if scam_probability <= RISK_HIGH_MAX:
            return "HIGH"
        return "CRITICAL"

    def save(
        self,
        classifier_path: Path | str = DEFAULT_CLASSIFIER_PATH,
        metadata_path: Path | str = DEFAULT_METADATA_PATH,
        extra_metadata: dict | None = None,
    ) -> None:
        """Serialize classifier and write metadata JSON."""
        clf_p = Path(classifier_path)
        meta_p = Path(metadata_path)

        clf_p.parent.mkdir(parents=True, exist_ok=True)
        meta_p.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.classifier, clf_p)

        meta = {
            "model_name": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "classes": self.classes_,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "c_param": self.c_param,
            "max_iter": self.max_iter,
            "class_weight": self.class_weight,
            "random_seed": self.random_state,
        }
        if extra_metadata:
            meta.update(extra_metadata)

        with open(meta_p, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        if Path(classifier_path) == Path(DEFAULT_CLASSIFIER_PATH):
            with self._lock:
                ScamClassifier._cached_classifier = self.classifier
                ScamClassifier._cached_metadata = meta

    @classmethod
    def load(
        cls,
        classifier_path: Path | str = DEFAULT_CLASSIFIER_PATH,
        metadata_path: Path | str = DEFAULT_METADATA_PATH,
        force_reload: bool = False,
    ) -> tuple[LogisticRegression, dict]:
        """Load serialized classifier using singleton cache."""
        clf_p = Path(classifier_path)
        meta_p = Path(metadata_path)

        with cls._lock:
            if not force_reload and cls._cached_classifier is not None and cls._cached_metadata is not None:
                return cls._cached_classifier, cls._cached_metadata

            if not clf_p.exists():
                raise NLPModelNotTrainedError(
                    f"NLP model artifact not found at '{clf_p}'. Run 'python scripts/train_scam_classifier.py' first."
                )

            classifier = joblib.load(clf_p)
            metadata = {}
            if meta_p.exists():
                try:
                    with open(meta_p, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                except Exception:
                    metadata = {"model_name": MODEL_NAME, "model_version": MODEL_VERSION}

            cls._cached_classifier = classifier
            cls._cached_metadata = metadata
            return classifier, metadata

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached singleton instance (useful for unit tests)."""
        with cls._lock:
            cls._cached_classifier = None
            cls._cached_metadata = None
