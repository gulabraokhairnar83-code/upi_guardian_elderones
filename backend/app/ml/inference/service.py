"""UPI Guardian - Anomaly Detection Inference Service.

Coordinates feature extraction, Isolation Forest inference, score normalization,
risk level assignment, and behavioral explainability.
"""

from pathlib import Path
import numpy as np

from app.ml.config import DEFAULT_METADATA_PATH, DEFAULT_MODEL_PATH, FEATURE_NAMES, MODEL_VERSION
from app.ml.explainability.explainer import BehavioralExplainer
from app.ml.features.extractor import FeatureExtractor
from app.ml.models.isolation_forest import IsolationForestModel, ModelNotTrainedError


class AnomalyDetectionService:
    """Performs real-time anomaly inference for candidate transactions."""

    def __init__(
        self,
        model_path: Path | str = DEFAULT_MODEL_PATH,
        metadata_path: Path | str = DEFAULT_METADATA_PATH,
    ):
        self.model_path = model_path
        self.metadata_path = metadata_path

    def analyze(
        self,
        transaction: dict,
        historical_stats: dict | None = None,
    ) -> dict:
        """Run complete anomaly detection pipeline on a transaction.

        Args:
            transaction: Transaction dictionary with amount, payee, time/timestamp, upiId, etc.
            historical_stats: User's historical profile (mean, std, known_payees, velocity).

        Returns:
            dict containing:
                - anomaly_score: float (0.0 - 100.0)
                - anomaly: bool (True if anomalous)
                - risk_level: str ('LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL')
                - raw_decision: float
                - model_version: str
                - features: dict of extracted feature values
                - contributing_factors: list of factors
                - explanation: str
                - recommended_action: str ('allow' | 'review' | 'block')

        Raises:
            ModelNotTrainedError: If model weights are not found on disk.
        """
        # 1. Feature extraction
        feature_dict = FeatureExtractor.extract_feature_dict(transaction, historical_stats)
        feature_vector = np.array([feature_dict[name] for name in FEATURE_NAMES], dtype=np.float64).reshape(1, -1)

        # 2. Model inference (loads once via thread-safe singleton)
        model, metadata = IsolationForestModel.load(
            model_path=self.model_path,
            metadata_path=self.metadata_path,
        )

        # 3. Decision function & prediction
        # decision_function: < 0 is anomaly, > 0 is inlier
        raw_decision = float(model.decision_function(feature_vector)[0])
        raw_pred = int(model.predict(feature_vector)[0])  # -1 = anomaly, 1 = normal
        is_anomaly = bool(raw_pred == -1)

        # 4. Normalized anomaly score (0 - 100)
        anomaly_score = IsolationForestModel.compute_anomaly_score(raw_decision)

        # 5. Risk Level classification
        risk_level = IsolationForestModel.determine_risk_level(anomaly_score)

        # 6. Behavioral explainability breakdown
        explain_result = BehavioralExplainer.explain(
            features=feature_dict,
            anomaly_score=anomaly_score,
            risk_level=risk_level,
            historical_stats=historical_stats,
        )

        model_version = metadata.get("model_version", MODEL_VERSION)

        return {
            "anomaly_score": anomaly_score,
            "anomaly": is_anomaly,
            "risk_level": risk_level,
            "raw_decision": round(raw_decision, 4),
            "model_version": model_version,
            "features": feature_dict,
            "contributing_factors": explain_result["contributing_factors"],
            "explanation": explain_result["explanation"],
            "recommended_action": explain_result["recommended_action"],
        }
