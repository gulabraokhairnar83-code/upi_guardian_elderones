"""UPI Guardian - Temporal Correlation Engine.

Discovers and correlates recent suspicious communications (SMS / call transcripts)
with upcoming or current transactions within a 120-minute lookback window.
"""

from datetime import datetime, timezone
import math
from typing import Any
from app.db.repositories.message_repository import MessageRepository
from app.risk_fusion.config import RiskFusionConfig
from app.risk_fusion.models import TemporalMatch


class TemporalCorrelationEngine:
    """Computes temporal proximity and correlation between communications and transactions."""

    @staticmethod
    def parse_timestamp(ts: Any) -> datetime | None:
        """Parse various timestamp representations into timezone-aware UTC datetime."""
        if ts is None:
            return None
        if isinstance(ts, datetime):
            if ts.tzinfo is None:
                return ts.replace(tzinfo=timezone.utc)
            return ts.astimezone(timezone.utc)
        if isinstance(ts, (int, float)):
            # Epoch seconds or milliseconds
            try:
                sec = ts / 1000.0 if ts > 1e11 else float(ts)
                return datetime.fromtimestamp(sec, tz=timezone.utc)
            except (ValueError, OSError):
                return None
        if isinstance(ts, str):
            clean_str = ts.strip()
            if not clean_str:
                return None
            try:
                # Handle 'Z' suffix
                normalized = clean_str.replace("Z", "+00:00")
                dt = datetime.fromisoformat(normalized)
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except ValueError:
                return None
        return None

    @classmethod
    def evaluate_candidate(
        cls,
        tx_dt: datetime,
        comm_dt: datetime,
        comm_risk: float,
        window_minutes: int = RiskFusionConfig.COMMUNICATION_TRANSACTION_WINDOW_MINUTES,
    ) -> tuple[float, float, bool]:
        """Compute temporal proximity and correlation score for a single communication.

        Returns:
            (correlation_score, delta_minutes, within_window)
        """
        delta_seconds = (tx_dt - comm_dt).total_seconds()
        delta_minutes = delta_seconds / 60.0

        # Communication occurred in the future relative to transaction, or outside window
        if delta_minutes < 0.0 or delta_minutes > float(window_minutes):
            return 0.0, delta_minutes, False

        # Linear proximity decay: 1.0 at 0 min, 0.5 at 60 min, ~0.0 at 120 min
        proximity_factor = 1.0 - (delta_minutes / float(window_minutes))
        correlation_score = proximity_factor * float(comm_risk)

        return round(correlation_score, 2), round(delta_minutes, 1), True

    @classmethod
    def find_temporal_correlation(
        cls,
        user_id: str,
        transaction_timestamp: Any,
        candidate_communications: list[dict] | None = None,
        message_repo: MessageRepository | None = None,
    ) -> TemporalMatch:
        """Find the most strongly correlated suspicious communication for a transaction.

        Args:
            user_id: Target user ID
            transaction_timestamp: ISO timestamp, datetime, or epoch of transaction
            candidate_communications: Pre-filtered communication dicts (for testing / mocking)
            message_repo: Optional MessageRepository instance for database queries

        Returns:
            TemporalMatch with highest proximity score and metadata.
        """
        tx_dt = cls.parse_timestamp(transaction_timestamp) or datetime.now(timezone.utc)

        # Retrieve messages
        if candidate_communications is not None:
            messages = candidate_communications
        else:
            repo = message_repo or MessageRepository()
            cursor = repo.collection.find({"user_id": user_id}).sort("analyzed_at", -1).limit(20)
            messages = repo.clean_docs(list(cursor))

        best_match = TemporalMatch()
        highest_score = -1.0

        for msg in messages:
            # 1. Ignore LOW-risk / NORMAL communications
            classification = (msg.get("classification") or "").upper()
            risk_level = (msg.get("risk_level") or msg.get("level") or "").upper()
            raw_prob = msg.get("scam_probability")
            if raw_prob is None:
                raw_prob = msg.get("risk_score", 0.0)
            comm_risk = float(raw_prob)

            if classification == "NORMAL" or risk_level in ("LOW", "SAFE") or comm_risk < 30.0:
                continue

            # 2. Extract and parse communication timestamp
            comm_ts = msg.get("analyzed_at") or msg.get("timestamp") or msg.get("created_at")
            comm_dt = cls.parse_timestamp(comm_ts)
            if not comm_dt:
                continue

            # 3. Calculate correlation
            corr_score, delta_min, within_window = cls.evaluate_candidate(
                tx_dt=tx_dt,
                comm_dt=comm_dt,
                comm_risk=comm_risk,
            )

            if within_window and corr_score > highest_score:
                highest_score = corr_score
                qualifies_boost = (
                    comm_risk >= RiskFusionConfig.CROSS_SIGNAL_MIN_COMM_RISK
                    and within_window
                )
                best_match = TemporalMatch(
                    temporal_score=corr_score,
                    delta_minutes=delta_min,
                    matched_communication_id=msg.get("id") or msg.get("message_id"),
                    matched_message_type=msg.get("message_type") or msg.get("type", "sms"),
                    matched_scam_probability=comm_risk,
                    within_window=True,
                    qualifies_for_boost=qualifies_boost,
                )

        return best_match
