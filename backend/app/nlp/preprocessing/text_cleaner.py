"""UPI Guardian - NLP Text Preprocessing Pipeline.

Provides robust, privacy-conscious text cleaning for SMS messages and phone call transcripts.

Guarantees:
- Safe handling of null, empty, or non-string inputs
- Normalization of whitespace, punctuation, and casing
- Preservation of high-value scam markers (OTP, UPI, PIN, KYC, APK, ANYDESK, etc.)
- Privacy-safe text hashing (SHA-256) and sensitive log masking
"""

import hashlib
import re


class TextCleaner:
    """Preprocesses raw communication text for NLP feature extraction."""

    URL_REGEX = re.compile(r"https?://\S+|www\.\S+|bit\.ly/\S+|tinyurl\.com/\S+", re.IGNORECASE)
    PHONE_REGEX = re.compile(r"(?:\+91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}\b|(?:\+91[\-\s]?)?[6-9]\d{9}\b", re.IGNORECASE)
    NUMERIC_OTP_REGEX = re.compile(r"\b\d{4,6}\b")
    WHITESPACE_REGEX = re.compile(r"\s+")
    PUNCTUATION_REGEX = re.compile(r"[^\w\s\-]")

    @classmethod
    def clean(cls, text: str | None) -> str:
        """Clean and normalize communication text for TF-IDF vectorization.

        Args:
            text: Raw input string from SMS or call transcript.

        Returns:
            Normalized lowercase string with standardized tokens.
        """
        if text is None:
            return ""

        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception:
                return ""

        raw = text.strip()
        if not raw:
            return ""

        # Lowercase
        cleaned = raw.lower()

        # Normalize URLs to token
        cleaned = cls.URL_REGEX.sub(" link_url ", cleaned)

        # Normalize Phone numbers
        cleaned = cls.PHONE_REGEX.sub(" phone_num ", cleaned)

        # Remove special noise punctuation while preserving hyphens and words
        cleaned = cls.PUNCTUATION_REGEX.sub(" ", cleaned)

        # Normalize multiple spaces into single space
        cleaned = cls.WHITESPACE_REGEX.sub(" ", cleaned).strip()

        return cleaned

    @classmethod
    def compute_hash(cls, text: str | None) -> str:
        """Compute SHA-256 hash of cleaned text for privacy-preserving deduplication."""
        cleaned = cls.clean(text)
        return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()

    @classmethod
    def mask_sensitive(cls, text: str | None) -> str:
        """Mask potential 4-6 digit OTPs and phone numbers for safe logging."""
        if not text:
            return ""
        masked = cls.NUMERIC_OTP_REGEX.sub("••••", str(text))
        masked = cls.PHONE_REGEX.sub("+91 ••••• •••••", masked)
        return masked
