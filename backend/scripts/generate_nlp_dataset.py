"""UPI Guardian - CLI Script to Generate NLP Training Dataset.

Usage:
    python scripts/generate_nlp_dataset.py [--samples 600] [--seed 42] [--output path/to/dataset.csv]
"""

import argparse
from pathlib import Path
import sys

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.nlp.data.dataset import ScamDatasetGenerator


def parse_args():
    parser = argparse.ArgumentParser(description="Generate synthetic scam communication training data.")
    parser.add_argument("--samples", type=int, default=600, help="Total samples to generate (default: 600)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument(
        "--output",
        type=str,
        default=str(BASE_DIR / "app" / "nlp" / "data" / "scam_dataset.csv"),
        help="Output CSV file path",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print("=" * 60)
    print("UPI GUARDIAN — NLP SCAM DATASET GENERATOR")
    print("=" * 60)
    print(f"Target Samples: {args.samples}")
    print(f"Random Seed:    {args.seed}")
    print(f"Output File:    {args.output}")

    generator = ScamDatasetGenerator(random_seed=args.seed, target_samples=args.samples)
    df = generator.generate()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print("\nGeneration Complete:")
    print(f"  Total records:    {len(df)}")
    print("  Class distribution:")
    for label, count in df["label"].value_counts().items():
        print(f"    - {label}: {count} ({count/len(df)*100:.1f}%)")
    print("  Message types:")
    for mtype, count in df["message_type"].value_counts().items():
        print(f"    - {mtype}: {count}")
    print(f"  Dataset saved to: {output_path.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
