"""UPI Guardian - CLI Script to Generate Synthetic Transaction Training Data.

Usage:
    python scripts/generate_training_data.py [--users 20] [--transactions 1500] [--anomaly-pct 0.08] [--seed 42] [--output path/to/dataset.csv]
"""

import argparse
from pathlib import Path
import sys

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.ml.data.synthetic_generator import SyntheticTransactionGenerator


def parse_args():
    parser = argparse.ArgumentParser(description="Generate synthetic transaction training data.")
    parser.add_argument("--users", type=int, default=15, help="Number of simulated users (default: 15)")
    parser.add_argument("--transactions", type=int, default=1200, help="Total transactions to generate (default: 1200)")
    parser.add_argument("--anomaly-pct", type=float, default=0.08, help="Anomaly ratio (default: 0.08)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument(
        "--output",
        type=str,
        default=str(BASE_DIR / "app" / "ml" / "data" / "synthetic_transactions.csv"),
        help="Output CSV file path",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print("=" * 60)
    print("UPI GUARDIAN — SYNTHETIC DATA GENERATOR")
    print("=" * 60)
    print(f"Users:               {args.users}")
    print(f"Total Transactions:  {args.transactions}")
    print(f"Anomaly Percentage:  {args.anomaly_pct * 100:.1f}%")
    print(f"Random Seed:         {args.seed}")
    print(f"Output File:         {args.output}")

    generator = SyntheticTransactionGenerator(
        num_users=args.users,
        num_transactions=args.transactions,
        anomaly_percentage=args.anomaly_pct,
        random_seed=args.seed,
    )

    df = generator.generate_dataset()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print("\nGeneration Complete:")
    print(f"  Rows generated:    {len(df)}")
    print(f"  Normal instances:  {(df['is_anomaly'] == 0).sum()}")
    print(f"  Anomaly instances: {(df['is_anomaly'] == 1).sum()}")
    print(f"  Dataset saved to:  {output_path.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
