"""UPI Guardian - CLI Script to Train and Serialize Isolation Forest Model.

Workflow:
1. Generate synthetic elderly transaction dataset
2. Extract the 5 numerical features (amount, z_score_deviation, velocity, is_new_payee, unusual_time)
3. Fit scikit-learn IsolationForest
4. Evaluate baseline distribution
5. Serialize model via joblib and save metadata JSON

Usage:
    python scripts/train_anomaly_model.py [--transactions 1500] [--contamination 0.08] [--seed 42]
"""

import argparse
from pathlib import Path
import sys

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.ml.config import (
    CONTAMINATION,
    DEFAULT_METADATA_PATH,
    DEFAULT_MODEL_PATH,
    FEATURE_NAMES,
    MODEL_VERSION,
    N_ESTIMATORS,
    RANDOM_STATE,
)
from app.ml.data.synthetic_generator import SyntheticTransactionGenerator
from app.ml.models.isolation_forest import IsolationForestModel


def parse_args():
    parser = argparse.ArgumentParser(description="Train Isolation Forest anomaly model.")
    parser.add_argument("--users", type=int, default=15, help="Number of simulated users (default: 15)")
    parser.add_argument("--transactions", type=int, default=1200, help="Total transactions to train on (default: 1200)")
    parser.add_argument("--contamination", type=float, default=CONTAMINATION, help=f"Contamination rate (default: {CONTAMINATION})")
    parser.add_argument("--n-estimators", type=int, default=N_ESTIMATORS, help=f"Number of trees (default: {N_ESTIMATORS})")
    parser.add_argument("--seed", type=int, default=RANDOM_STATE, help=f"Random seed (default: {RANDOM_STATE})")
    parser.add_argument("--model-out", type=str, default=str(DEFAULT_MODEL_PATH), help="Model destination path")
    parser.add_argument("--meta-out", type=str, default=str(DEFAULT_METADATA_PATH), help="Metadata destination path")
    return parser.parse_args()


def main():
    args = parse_args()
    print("=" * 65)
    print("UPI GUARDIAN — ISOLATION FOREST MODEL TRAINING")
    print("=" * 65)

    print("\n[Step 1/4] Generating synthetic elderly transaction baseline...")
    generator = SyntheticTransactionGenerator(
        num_users=args.users,
        num_transactions=args.transactions,
        anomaly_percentage=args.contamination,
        random_seed=args.seed,
    )
    df = generator.generate_dataset()
    print(f"  Generated {len(df)} transactions across {args.users} user profiles.")

    print("\n[Step 2/4] Extracting feature matrix...")
    X = df[FEATURE_NAMES].to_numpy(dtype=float)
    print(f"  Feature shape: {X.shape}")
    print(f"  Features:      {', '.join(FEATURE_NAMES)}")

    print("\n[Step 3/4] Fitting Isolation Forest ensemble...")
    model_mgr = IsolationForestModel(
        n_estimators=args.n_estimators,
        contamination=args.contamination,
        random_state=args.seed,
        model_version=MODEL_VERSION,
    )
    summary = model_mgr.train(X)

    print("\n[Step 4/4] Serializing model artifact and writing metadata...")
    model_mgr.save(
        model_path=args.model_out,
        metadata_path=args.meta_out,
        extra_metadata=summary,
    )

    print("\n" + "=" * 65)
    print("TRAINING SUMMARY REPORT")
    print("=" * 65)
    print(f"  Model Type:             {summary['model_type']}")
    print(f"  Model Version:          {summary['version']}")
    print(f"  Number of Records:      {summary['n_samples']}")
    print(f"  Number of Features:     {summary['n_features']}")
    print(f"  Feature Names:          {', '.join(summary['feature_names'])}")
    print(f"  Contamination:          {summary['contamination']}")
    print(f"  Estimators (Trees):     {summary['n_estimators']}")
    print(f"  Random Seed:            {summary['random_state']}")
    print(f"  Detected Anomalies:     {summary['anomalies_detected_in_train']} ({summary['anomaly_rate'] * 100:.2f}%)")
    print(f"  Decision Score Min:     {summary['decision_min']}")
    print(f"  Decision Score Max:     {summary['decision_max']}")
    print(f"  Decision Score Mean:    {summary['decision_mean']}")
    print(f"  Saved Model Path:       {Path(args.model_out).resolve()}")
    print(f"  Saved Metadata Path:    {Path(args.meta_out).resolve()}")
    print("=" * 65)
    print("Training successfully finished.\n")


if __name__ == "__main__":
    main()
