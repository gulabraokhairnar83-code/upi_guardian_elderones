"""UPI Guardian - NLP Scam Detection Inference Service.

Coordinates text preprocessing, TF-IDF feature transformation,
Logistic Regression classification, probability calibration, and explainability.
"""

from pathlib import Path
from app.nlp.config import (
    DEFAULT_CLASSIFIER_PATH,
    DEFAULT_METADATA_PATH,
    DEFAULT_VECTORIZER_PATH,
    MODEL_VERSION,
)
from app.nlp.explainability.explainer import ScamExplainer
from app.nlp.features.tfidf import TfidfFeatureExtractor
from app.nlp.models.scam_classifier import NLPModelNotTrainedError, ScamClassifier
from app.nlp.preprocessing.text_cleaner import TextCleaner


class NLPScamDetectionService:
    """Performs real-time scam communication inference on SMS and call transcript texts."""

    def __init__(
        self,
        classifier_path: Path | str = DEFAULT_CLASSIFIER_PATH,
        vectorizer_path: Path | str = DEFAULT_VECTORIZER_PATH,
        metadata_path: Path | str = DEFAULT_METADATA_PATH,
    ):
        self.classifier_path = classifier_path
        self.vectorizer_path = vectorizer_path
        self.metadata_path = metadata_path
        self._vectorizer = None

    def _get_vectorizer(self) -> TfidfFeatureExtractor:
        """Load vectorizer artifact using local cache."""
        if self._vectorizer is None:
            v_path = Path(self.vectorizer_path)
            if not v_path.exists():
                raise NLPModelNotTrainedError(
                    f"TF-IDF vectorizer artifact not found at '{v_path}'. Train NLP model first."
                )
            self._vectorizer = TfidfFeatureExtractor.load(v_path)
        return self._vectorizer

    def analyze(self, text: str, message_type: str = "sms") -> dict:
        """Run complete NLP scam analysis pipeline on communication text.

        Args:
            text: Raw input text from SMS or call transcript.
            message_type: 'sms' or 'call_transcript'.

        Returns:
            dict containing:
                - classification: 'NORMAL' | 'SUSPICIOUS' | 'SCAM'
                - scam_probability: float (0.0 to 100.0)
                - risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
                - message_type: str
                - class_probabilities: dict[str, float]
                - categories: list[str]
                - suspicious_phrases: list[str]
                - explanation: str
                - recommended_action: str
                - model_version: str
                - text_hash: str

        Raises:
            NLPModelNotTrainedError: If serialized model or vectorizer artifact is missing.
        """
        # 1. Clean and normalize text
        cleaned_text = TextCleaner.clean(text)
        text_hash = TextCleaner.compute_hash(text)

        # 2. Load vectorizer & classifier
        vectorizer = self._get_vectorizer()
        classifier, metadata = ScamClassifier.load(
            classifier_path=self.classifier_path,
            metadata_path=self.metadata_path,
        )

        # 3. TF-IDF feature transformation
        X = vectorizer.transform(cleaned_text)

        # 4. Classifier prediction & probabilities
        class_probs = {}
        probas = classifier.predict_proba(X)[0]
        for idx, cls_name in enumerate(classifier.classes_):
            class_probs[cls_name] = round(float(probas[idx]), 4)

        pred_class = str(classifier.predict(X)[0])

        # 5. Calculate normalized 0-100 scam risk probability
        scam_prob = ScamClassifier.compute_scam_probability(class_probs)

        # 6. Determine risk level
        risk_level = ScamClassifier.determine_risk_level(scam_prob, pred_class)

        # 7. Generate explainability (categories, phrases, advice)
        explanation_data = ScamExplainer.explain(
            text=text,
            classification=pred_class,
            scam_probability=scam_prob,
            risk_level=risk_level,
        )

        model_version = metadata.get("model_version", MODEL_VERSION)

        return {
            "classification": pred_class,
            "scam_probability": scam_prob,
            "risk_level": risk_level,
            "message_type": message_type,
            "class_probabilities": class_probs,
            "categories": explanation_data["categories"],
            "suspicious_phrases": explanation_data["suspicious_phrases"],
            "explanation": explanation_data["explanation"],
            "recommended_action": explanation_data["recommended_action"],
            "model_version": model_version,
            "text_hash": text_hash,
        }
