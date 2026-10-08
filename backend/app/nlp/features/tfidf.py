"""UPI Guardian - TF-IDF Feature Extraction Module.

Wraps scikit-learn's TfidfVectorizer for unigram and bigram representation of
communication text in SMS messages and phone call transcripts.
"""

from pathlib import Path
import joblib
from scipy.sparse import spmatrix
from sklearn.feature_extraction.text import TfidfVectorizer

from app.nlp.config import (
    DEFAULT_VECTORIZER_PATH,
    TFIDF_MAX_FEATURES,
    TFIDF_MIN_DF,
    TFIDF_NGRAM_RANGE,
    TFIDF_SUBLINEAR_TF,
)


class TfidfFeatureExtractor:
    """Manages TF-IDF vectorization training, serialization, loading, and inference transform."""

    def __init__(
        self,
        max_features: int = TFIDF_MAX_FEATURES,
        ngram_range: tuple[int, int] = TFIDF_NGRAM_RANGE,
        sublinear_tf: bool = TFIDF_SUBLINEAR_TF,
        min_df: int = TFIDF_MIN_DF,
    ):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            sublinear_tf=sublinear_tf,
            min_df=min_df,
            lowercase=True,
            strip_accents="unicode",
        )
        self.is_fitted = False

    def fit(self, texts: list[str]) -> "TfidfFeatureExtractor":
        """Fit vectorizer on a corpus of cleaned training texts."""
        self.vectorizer.fit(texts)
        self.is_fitted = True
        return self

    def transform(self, texts: list[str] | str) -> spmatrix:
        """Transform text or list of texts into TF-IDF sparse matrix."""
        if isinstance(texts, str):
            texts = [texts]
        return self.vectorizer.transform(texts)

    def fit_transform(self, texts: list[str]) -> spmatrix:
        """Fit on texts and transform them into TF-IDF representation."""
        matrix = self.vectorizer.fit_transform(texts)
        self.is_fitted = True
        return matrix

    def save(self, filepath: Path | str = DEFAULT_VECTORIZER_PATH) -> None:
        """Serialize fitted vectorizer using joblib."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, path)

    @classmethod
    def load(cls, filepath: Path | str = DEFAULT_VECTORIZER_PATH) -> "TfidfFeatureExtractor":
        """Load serialized vectorizer from disk."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"TF-IDF vectorizer artifact not found at '{path}'.")
        extractor = cls()
        extractor.vectorizer = joblib.load(path)
        extractor.is_fitted = True
        return extractor
