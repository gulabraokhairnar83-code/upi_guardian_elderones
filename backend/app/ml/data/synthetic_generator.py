"""UPI Guardian - Synthetic Transaction Data Generator.

Generates reproducible synthetic UPI transaction datasets representing
elderly-user behavioral patterns and controlled anomaly distributions.

Categories:
- groceries
- medicines
- electricity bills
- mobile recharge
- gas
- rent
- family transfers
- shopping
- utility payments
"""

from datetime import datetime, timedelta, timezone
import random
import numpy as np
import pandas as pd

from app.ml.config import FEATURE_NAMES, UNUSUAL_HOURS
from app.ml.features.extractor import FeatureExtractor

# Typical category configurations for elderly Indian users
CATEGORIES = {
    "groceries": {"min": 150, "max": 2500, "typical_mean": 950, "typical_std": 400},
    "medicines": {"min": 200, "max": 4000, "typical_mean": 1400, "typical_std": 600},
    "electricity bills": {"min": 800, "max": 3500, "typical_mean": 1800, "typical_std": 500},
    "mobile recharge": {"min": 199, "max": 800, "typical_mean": 399, "typical_std": 150},
    "gas": {"min": 750, "max": 1300, "typical_mean": 950, "typical_std": 150},
    "rent": {"min": 8000, "max": 22000, "typical_mean": 14000, "typical_std": 3000},
    "family transfers": {"min": 500, "max": 8000, "typical_mean": 3000, "typical_std": 1500},
    "shopping": {"min": 300, "max": 3500, "typical_mean": 1200, "typical_std": 700},
    "utility payments": {"min": 300, "max": 2000, "typical_mean": 850, "typical_std": 350},
}

KNOWN_MERCHANTS = [
    "Fresh Basket Groceries",
    "City Care Pharmacy",
    "Apollo Meds",
    "MahaVitaran Electricity",
    "Airtel Prepaid Recharge",
    "Jio Mobile Care",
    "Bharat Gas Agency",
    "Apna Kirana Store",
    "Pune Municipal Water",
    "D-Mart Supermarket",
]

KNOWN_FAMILY_NAMES = [
    "Rajesh (Son)",
    "Kavita (Daughter)",
    "Amit (Grandson)",
    "Pooja (Daughter-in-law)",
]

SUSPICIOUS_PAYEES = [
    "QuickLoan Support Agent",
    "Lottery Prize Claim Dept",
    "KYC Verification Official",
    "Unknown Crypto Trader",
    "Urgent Cash Desk",
    "Reward Point Redemption",
    "FastCash Processing",
    "Overseas Gift Clearance",
]


class SyntheticTransactionGenerator:
    """Generates synthetic elderly transaction histories and anomalous testing instances."""

    def __init__(
        self,
        num_users: int = 15,
        num_transactions: int = 1200,
        anomaly_percentage: float = 0.08,
        random_seed: int = 42,
    ):
        self.num_users = max(1, num_users)
        self.num_transactions = max(50, num_transactions)
        self.anomaly_percentage = min(max(0.0, anomaly_percentage), 0.5)
        self.random_seed = random_seed
        self.rng = random.Random(random_seed)
        self.np_rng = np.random.default_rng(random_seed)

    def _generate_user_profiles(self) -> dict[str, dict]:
        """Generate baseline profiles for synthetic elderly users."""
        users = {}
        for i in range(self.num_users):
            user_id = f"usr_elder_{100 + i}"
            base_mean = self.rng.uniform(1600.0, 3200.0)
            base_std = self.rng.uniform(600.0, 1400.0)
            # Pick a subset of recurring payees for this user
            merchants = self.rng.sample(KNOWN_MERCHANTS, k=min(5, len(KNOWN_MERCHANTS)))
            family = self.rng.sample(KNOWN_FAMILY_NAMES, k=min(2, len(KNOWN_FAMILY_NAMES)))
            users[user_id] = {
                "user_id": user_id,
                "historical_mean": round(base_mean, 2),
                "historical_std": round(base_std, 2),
                "known_payees": set(merchants + family),
            }
        return users

    def generate_dataset(self) -> pd.DataFrame:
        """Generate a complete reproducible synthetic dataset.

        Returns:
            pandas DataFrame containing raw transaction fields and extracted features.
        """
        users = self._generate_user_profiles()
        user_ids = list(users.keys())

        num_anomalies = int(self.num_transactions * self.anomaly_percentage)
        num_normals = self.num_transactions - num_anomalies

        records = []
        base_time = datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc)

        # 1. Normal Transactions
        for i in range(num_normals):
            user_id = self.rng.choice(user_ids)
            user_profile = users[user_id]
            category = self.rng.choice(list(CATEGORIES.keys()))
            cat_cfg = CATEGORIES[category]

            # Sample amount around category mean within user baseline
            raw_amt = self.np_rng.normal(cat_cfg["typical_mean"], cat_cfg["typical_std"])
            amount = max(cat_cfg["min"], min(cat_cfg["max"] * 1.5, raw_amt))
            amount = round(float(amount), 2)

            # Normal hours: 07:00 to 21:00
            hour = self.rng.randint(7, 21)
            minute = self.rng.randint(0, 59)
            day_offset = self.rng.randint(0, 30)
            txn_time = base_time + timedelta(days=day_offset, hours=hour - 9, minutes=minute)

            # Known payee (92% known, 8% benign new small payee like occasional tea shop)
            if self.rng.random() < 0.92:
                payee = self.rng.choice(list(user_profile["known_payees"]))
                is_new_payee = 0
            else:
                payee = f"Local Store {self.rng.randint(1, 20)}"
                is_new_payee = 1

            # Normal velocity
            velocity = 1 if self.rng.random() < 0.85 else 2
            unusual_time = 0

            # Compute z_score safely
            z_score = FeatureExtractor.calculate_z_score(
                amount,
                user_profile["historical_mean"],
                user_profile["historical_std"],
            )

            records.append({
                "transaction_id": f"TXN-SYN-NORM-{i+1:05d}",
                "user_id": user_id,
                "category": category,
                "payee": payee,
                "amount": amount,
                "timestamp": txn_time.isoformat(),
                "time_str": txn_time.strftime("%I:%M %p"),
                "velocity": velocity,
                "is_new_payee": is_new_payee,
                "unusual_time": unusual_time,
                "z_score_deviation": round(z_score, 4),
                "is_anomaly": 0,
                "anomaly_type": "none",
            })

        # 2. Anomaly Transactions (diversified patterns)
        for j in range(num_anomalies):
            user_id = self.rng.choice(user_ids)
            user_profile = users[user_id]
            anomaly_type = self.rng.choice([
                "huge_amount_new_payee",
                "rapid_velocity_burst",
                "late_night_urgent",
                "extreme_zscore_transfer",
                "multi_factor_suspicious",
            ])

            day_offset = self.rng.randint(0, 30)

            if anomaly_type == "huge_amount_new_payee":
                amount = round(float(self.rng.uniform(35000.0, 92000.0)), 2)
                payee = self.rng.choice(SUSPICIOUS_PAYEES)
                is_new_payee = 1
                hour = self.rng.randint(9, 20)
                unusual_time = 0
                velocity = self.rng.randint(1, 2)
                category = "shopping"

            elif anomaly_type == "rapid_velocity_burst":
                amount = round(float(self.rng.uniform(12000.0, 30000.0)), 2)
                payee = self.rng.choice(SUSPICIOUS_PAYEES)
                is_new_payee = 1
                hour = self.rng.randint(10, 18)
                unusual_time = 0
                velocity = self.rng.randint(4, 7)  # rapid repeated transactions
                category = "family transfers"

            elif anomaly_type == "late_night_urgent":
                amount = round(float(self.rng.uniform(18000.0, 55000.0)), 2)
                payee = self.rng.choice(SUSPICIOUS_PAYEES)
                is_new_payee = 1
                hour = self.rng.choice([23, 0, 1, 2, 3, 4])  # unusual late night hour
                unusual_time = 1
                velocity = self.rng.randint(2, 4)
                category = "utility payments"

            elif anomaly_type == "extreme_zscore_transfer":
                # 8x to 15x historical standard deviation
                amount = round(user_profile["historical_mean"] + (user_profile["historical_std"] * self.rng.uniform(5.5, 12.0)), 2)
                payee = f"Private Account {self.rng.randint(100, 999)}"
                is_new_payee = 1
                hour = self.rng.randint(8, 21)
                unusual_time = 0
                velocity = 2
                category = "family transfers"

            else:  # multi_factor_suspicious
                amount = round(float(self.rng.uniform(22000.0, 65000.0)), 2)
                payee = self.rng.choice(SUSPICIOUS_PAYEES)
                is_new_payee = 1
                hour = self.rng.choice([23, 1, 2])
                unusual_time = 1
                velocity = self.rng.randint(3, 5)
                category = "shopping"

            txn_time = base_time + timedelta(days=day_offset, hours=hour - 9, minutes=self.rng.randint(0, 59))

            z_score = FeatureExtractor.calculate_z_score(
                amount,
                user_profile["historical_mean"],
                user_profile["historical_std"],
            )

            records.append({
                "transaction_id": f"TXN-SYN-ANOM-{j+1:05d}",
                "user_id": user_id,
                "category": category,
                "payee": payee,
                "amount": amount,
                "timestamp": txn_time.isoformat(),
                "time_str": txn_time.strftime("%I:%M %p"),
                "velocity": velocity,
                "is_new_payee": is_new_payee,
                "unusual_time": unusual_time,
                "z_score_deviation": round(z_score, 4),
                "is_anomaly": 1,
                "anomaly_type": anomaly_type,
            })

        # Shuffle deterministically
        self.rng.shuffle(records)
        df = pd.DataFrame(records)

        # Enforce all 5 required features are non-null and numeric
        for col in FEATURE_NAMES:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        return df
