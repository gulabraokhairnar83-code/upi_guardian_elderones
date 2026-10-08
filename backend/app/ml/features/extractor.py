"""UPI Guardian - Feature Extraction Pipeline.

Extracts the 5 numerical features required by the Isolation Forest model:
1. amount: Transaction amount (INR)
2. z_score_deviation: Normalized deviation from user's historical average
3. velocity: Transaction count in the preceding 1-hour window
4. is_new_payee: Binary indicator (0 = known payee, 1 = new payee)
5. unusual_time: Binary indicator (0 = normal daytime hours, 1 = late night 23:00-05:00)

Guarantees:
- Safe handling of zero historical standard deviation or missing history
- No NaN, null, or infinite values in feature vectors
- Deterministic extraction
"""

import math
import re
from datetime import datetime, timezone
import numpy as np

from app.ml.config import FEATURE_NAMES, UNUSUAL_HOURS


class FeatureExtractor:
    """Extracts and validates features for transaction anomaly detection."""

    @classmethod
    def extract_features(
        cls,
        transaction: dict,
        historical_stats: dict | None = None,
    ) -> np.ndarray:
        """Extract a 1D numpy array of length 5 matching FEATURE_NAMES.

        Args:
            transaction: Dictionary containing transaction data (amount, time/timestamp, payee, etc.)
            historical_stats: Dictionary containing historical context:
                - 'mean': float, average historical amount
                - 'std': float, standard deviation of historical amounts
                - 'known_payees': set or list of previously paid names/UPI IDs
                - 'velocity': int, recent transaction frequency (optional, defaults to transaction's velocity)

        Returns:
            np.ndarray of shape (5,) with float64 values, guaranteed finite.
        """
        feature_dict = cls.extract_feature_dict(transaction, historical_stats)
        vector = np.array([feature_dict[name] for name in FEATURE_NAMES], dtype=np.float64)

        # Enforce finite guarantee
        if np.isnan(vector).any() or np.isinf(vector).any():
            vector = np.nan_to_num(vector, nan=0.0, posinf=9999.0, neginf=-9999.0)

        return vector

    @classmethod
    def extract_feature_dict(
        cls,
        transaction: dict,
        historical_stats: dict | None = None,
    ) -> dict[str, float]:
        """Extract features as a dictionary mapped to feature names.

        Args:
            transaction: Transaction data dictionary.
            historical_stats: User's historical behavioral statistics.

        Returns:
            dict with keys: 'amount', 'z_score_deviation', 'velocity', 'is_new_payee', 'unusual_time'
        """
        stats = historical_stats or {}

        # 1. Amount
        raw_amount = transaction.get("amount", 0.0)
        try:
            amount = float(raw_amount)
            if math.isnan(amount) or math.isinf(amount) or amount < 0:
                amount = 0.0
        except (ValueError, TypeError):
            amount = 0.0

        # 2. Z-Score Deviation
        # Safely compute (amount - mean) / std.
        # If std is 0.0, None, or unavailable, deviation is 0.0.
        mean = stats.get("mean")
        std = stats.get("std")

        z_score = cls.calculate_z_score(amount, mean, std)

        # 3. Velocity (transactions in the preceding 1-hour window)
        raw_velocity = stats.get("velocity", transaction.get("velocity", 1))
        try:
            velocity = float(raw_velocity)
            if math.isnan(velocity) or math.isinf(velocity) or velocity < 0:
                velocity = 1.0
        except (ValueError, TypeError):
            velocity = 1.0

        # 4. is_new_payee (0 = known, 1 = new)
        is_new_payee = cls.detect_new_payee(
            payee=transaction.get("payee", ""),
            upi_id=transaction.get("upiId", transaction.get("upi_id", "")),
            known_payees=stats.get("known_payees"),
            explicit_flag=transaction.get("is_new_payee", transaction.get("newPayee")),
        )

        # 5. unusual_time (0 = normal, 1 = unusual hours 23:00-05:00)
        unusual_time = cls.detect_unusual_time(
            timestamp=transaction.get("timestamp"),
            time_str=transaction.get("time"),
            explicit_flag=transaction.get("unusual_time"),
        )

        return {
            "amount": round(amount, 2),
            "z_score_deviation": round(z_score, 4),
            "velocity": round(velocity, 2),
            "is_new_payee": float(is_new_payee),
            "unusual_time": float(unusual_time),
        }

    @staticmethod
    def calculate_z_score(
        amount: float,
        mean: float | None,
        std: float | None,
    ) -> float:
        """Safely compute z-score deviation.

        If std is 0, None, negative, or mean is None, returns 0.0 to prevent division by zero or NaN.
        """
        if mean is None or std is None:
            return 0.0

        try:
            mean_f = float(mean)
            std_f = float(std)
            if std_f <= 0.0 or math.isnan(std_f) or math.isinf(std_f):
                return 0.0
            if math.isnan(mean_f) or math.isinf(mean_f):
                return 0.0

            z = (amount - mean_f) / std_f
            if math.isnan(z) or math.isinf(z):
                return 0.0
            return float(z)
        except (ValueError, TypeError, ZeroDivisionError):
            return 0.0

    @staticmethod
    def detect_new_payee(
        payee: str,
        upi_id: str,
        known_payees: set | list | None,
        explicit_flag: bool | int | None = None,
    ) -> int:
        """Determine if payee is new to this user.

        Returns 1 if new payee, 0 if known payee.
        """
        if explicit_flag is not None:
            return 1 if bool(explicit_flag) else 0

        if known_payees is None:
            # If no history is provided, check if payee string is present
            return 0

        payee_clean = str(payee).strip().lower()
        upi_clean = str(upi_id).strip().lower()

        known_set = {str(k).strip().lower() for k in known_payees}

        if (payee_clean and payee_clean in known_set) or (upi_clean and upi_clean in known_set):
            return 0
        return 1

    @staticmethod
    def detect_unusual_time(
        timestamp: str | None = None,
        time_str: str | None = None,
        explicit_flag: bool | int | None = None,
    ) -> int:
        """Determine if the transaction occurred during unusual hours (23:00 to 05:00).

        Returns 1 if unusual time, 0 otherwise.
        """
        if explicit_flag is not None:
            return 1 if bool(explicit_flag) else 0

        # Try parsing ISO timestamp first
        if timestamp:
            try:
                # Handle formats like "2026-09-29T23:15:00Z" or "2026-09-29 23:15:00"
                cleaned = str(timestamp).replace("Z", "+00:00")
                dt = datetime.fromisoformat(cleaned)
                return 1 if dt.hour in UNUSUAL_HOURS else 0
            except (ValueError, TypeError):
                pass

        # Try parsing time_str like "11:42 PM" or "23:42"
        if time_str:
            ts = str(time_str).strip().upper()
            # 12-hour AM/PM format (e.g., "11:42 PM")
            match_12 = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)$", ts)
            if match_12:
                hour = int(match_12.group(1))
                period = match_12.group(3)
                if period == "PM" and hour != 12:
                    hour += 12
                elif period == "AM" and hour == 12:
                    hour = 0
                return 1 if hour in UNUSUAL_HOURS else 0

            # 24-hour format (e.g., "23:42")
            match_24 = re.match(r"^(\d{1,2}):(\d{2})", ts)
            if match_24:
                hour = int(match_24.group(1))
                return 1 if hour in UNUSUAL_HOURS else 0

        # Default to normal hours if no time information is available
        return 0
