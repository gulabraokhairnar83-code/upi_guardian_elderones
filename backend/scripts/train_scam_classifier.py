"""UPI Guardian - CLI Script to Train and Serialize NLP Scam Classifier.

Workflow:
1. Generate synthetic scam communication dataset
2. Split into train and test sets (stratified)
3. Fit TF-IDF Vectorizer on train texts
4. Train Logistic Regression classifier on TF-IDF features
5. Evaluate model on test set (accuracy, precision, recall, F1, confusion matrix)
6. Serialize vectorizer, classifier, and metadata JSON

Usage:
    python scripts/train_scam_classifier.py [--samples 600] [--seed 42]
"""

import argparse
from pathlib import Path
import sys
from sklearn.model_selection import train_test_split

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.nlp.config import (
    DEFAULT_CLASSIFIER_PATH,
    DEFAULT_METADATA_PATH,
    DEFAULT_VECTORIZER_PATH,
    MODEL_VERSION,
    RANDOM_SEED,
)
from app.nlp.data.dataset import ScamDatasetGenerator
from app.nlp.features.tfidf import TfidfFeatureExtractor
from app.nlp.models.scam_classifier import ScamClassifier


def parse_args():
    parser = argparse.ArgumentParser(description="Train NLP scam communication classifier.")
    parser.add_argument("--samples", type=int, default=600, help="Total dataset size (default: 600)")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED, help=f"Random seed (default: {RANDOM_SEED})")
    parser.add_argument("--test-size", type=float, default=0.25, help="Test set fraction (default: 0.25)")
    return parser.parse_args()


def main():
    args = parse_args()
    print("=" * 65)
    print("UPI GUARDIAN — NLP SCAM CLASSIFIER TRAINING")
    print("=" * 65)

    print("\n[Step 1/4] Generating balanced synthetic communication dataset...")
    generator = ScamDatasetGenerator(random_seed=args.seed, target_samples=args.samples)
    df = generator.generate()
    print(f"  Generated {len(df)} records across {df['label'].nunique()} classes.")

    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        df["cleaned_text"].tolist(),
        df["label"].tolist(),
        test_size=args.test_size,
        random_state=args.seed,
        stratify=df["label"].tolist(),
    )
    print(f"  Train set: {len(X_train_raw)} samples | Test set: {len(X_test_raw)} samples")

    print("\n[Step 2/4] Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfFeatureExtractor()
    X_train_tfidf = vectorizer.fit_transform(X_train_raw)
    X_test_tfidf = vectorizer.transform(X_test_raw)
    print(f"  Vocabulary size: {X_train_tfidf.shape[1]} n-gram features")

    print("\n[Step 3/4] Fitting Logistic Regression classifier...")
    classifier = ScamClassifier(random_state=args.seed)
    classifier.train(X_train_tfidf, y_train)

    print("\n[Step 4/4] Evaluating classifier performance on test set...")
    eval_metrics = classifier.evaluate(X_test_tfidf, y_test)

    print("\n" + "=" * 65)
    print("MODEL EVALUATION REPORT")
    print("=" * 65)
    print(f"  Overall Accuracy: {eval_metrics['accuracy'] * 100:.2f}%\n")
    print("  Classification Metrics per Class:")
    report = eval_metrics["classification_report"]
    for cls_name in eval_metrics["classes"]:
        if cls_name in report:
            p = report[cls_name]["precision"]
            r = report[cls_name]["recall"]
            f1 = report[cls_name]["f1-score"]
            support = int(report[cls_name]["support"])
            print(f"    - {cls_name:<11}: Precision={p:.2f}, Recall={r:.2f}, F1={f1:.2f} (n={support})")

    print("\n  Confusion Matrix (rows=actual, cols=pred):")
    conf_mat = eval_metrics["confusion_matrix"]
    header = "       " + "  ".join([f"{c[:4]:>6}" for c in eval_metrics["classes"]])
    print(header)
    for idx, row in enumerate(conf_mat):
        row_str = "  ".join([f"{val:>6}" for val in row])
        print(f"  {eval_metrics['classes'][idx][:4]:<4} {row_str}")

    print("\n  NOTE: Evaluation results are based on the synthetic/legal demonstration")
    print("  dataset and should not be interpreted as real-world fraud detection accuracy.")

    print("\n[Step 5/5] Serializing artifacts to disk...")
    vectorizer.save(DEFAULT_VECTORIZER_PATH)
    classifier.save(
        classifier_path=DEFAULT_CLASSIFIER_PATH,
        metadata_path=DEFAULT_METADATA_PATH,
        extra_metadata={
            "metrics": {
                "accuracy": eval_metrics["accuracy"],
                "macro_f1": round(report["macro avg"]["f1-score"], 4),
                "weighted_f1": round(report["weighted avg"]["f1-score"], 4),
            },
            "train_samples": len(X_train_raw),
            "test_samples": len(X_test_raw),
            "features_count": X_train_tfidf.shape[1],
        },
    )

    print(f"  Saved Vectorizer: {Path(DEFAULT_VECTORIZER_PATH).resolve()}")
    print(f"  Saved Classifier: {Path(DEFAULT_CLASSIFIER_PATH).resolve()}")
    print(f"  Saved Metadata:   {Path(DEFAULT_METADATA_PATH).resolve()}")
    print("=" * 65)
    print("NLP Training successfully finished.\n")


if __name__ == "__main__":
    main()
