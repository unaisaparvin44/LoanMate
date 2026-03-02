"""
LoanMate — ML Training Pipeline
================================
Trains a RandomForestClassifier on historical loan decisions exported as CSV.

Usage:
    python train_model.py --data <path_to_csv> [--model <output_model_path>]

Constraints:
    - Rows where status = 'Pending' are excluded (no ground-truth label).
    - reviewed_by and timestamp columns are dropped (leakage prevention).
    - No Django dependencies.
    - Model output is decision-support only. It does NOT automate approvals.
"""

import argparse
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)


# ── Constants ────────────────────────────────────────────────────────────────

# Columns the officer decided on — the sole ground truth
TARGET_COLUMN = "status"

# Columns that encode officer identity or time — must never be features
LEAKAGE_COLUMNS = ["reviewed_by", "created_at", "reviewed_at"]

# The two valid training labels (Pending rows are excluded before this mapping)
LABEL_MAP = {"Approved": 1, "Rejected": 0}

# Feature columns expected in the CSV
CATEGORICAL_FEATURES = ["loan_type", "employment"]
NUMERICAL_FEATURES = ["income", "amount"]

RANDOM_SEED = 42
TEST_SIZE = 0.2


# ── Data Loading & Cleaning ──────────────────────────────────────────────────

def load_and_clean(csv_path: str) -> pd.DataFrame:
    """
    Load the CSV and apply safety filters:
      1. Drop rows with status = 'Pending' (no ground truth).
      2. Drop timestamp and reviewer columns (data leakage).
      3. Drop any remaining rows with nulls in required columns.
    """
    df = pd.read_csv(csv_path)

    print(f"[INFO] Raw dataset shape: {df.shape}")

    # Step 1 — Exclude Pending rows
    pending_count = (df[TARGET_COLUMN] == "Pending").sum()
    df = df[df[TARGET_COLUMN] != "Pending"].copy()
    print(f"[INFO] Excluded {pending_count} Pending rows. Remaining: {len(df)}")

    if len(df) == 0:
        print("[ERROR] No training rows remain after excluding Pending. Exiting.")
        sys.exit(1)

    # Step 2 — Drop leakage columns (ignore if absent in this export)
    cols_to_drop = [c for c in LEAKAGE_COLUMNS if c in df.columns]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
        print(f"[INFO] Dropped leakage columns: {cols_to_drop}")

    # Step 3 — Validate required columns are present
    required = CATEGORICAL_FEATURES + NUMERICAL_FEATURES + [TARGET_COLUMN]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"[ERROR] Missing required columns: {missing}")
        sys.exit(1)

    # Step 4 — Drop rows with nulls in required columns
    before = len(df)
    df = df.dropna(subset=required)
    dropped = before - len(df)
    if dropped:
        print(f"[WARNING] Dropped {dropped} rows with null values in required columns.")

    return df


# ── Feature Engineering ──────────────────────────────────────────────────────

def encode_features(df: pd.DataFrame):
    """
    Encode categorical features using LabelEncoder.
    Returns the feature matrix X, target vector y, and fitted encoders dict.
    No feature engineering beyond encoding is applied.
    """
    encoders = {}
    df_encoded = df.copy()

    for col in CATEGORICAL_FEATURES:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
        encoders[col] = le

    # Map target labels to binary integers
    df_encoded[TARGET_COLUMN] = df_encoded[TARGET_COLUMN].map(LABEL_MAP)

    X = df_encoded[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
    y = df_encoded[TARGET_COLUMN]

    return X, y, encoders


# ── Training & Evaluation ────────────────────────────────────────────────────

def train_and_evaluate(X, y, confusion_matrix_path: str = None,
                       feature_importance_path: str = None):
    """
    Split data, train RandomForestClassifier, and print evaluation metrics.
    Computes accuracy, precision, recall, F1, and a confusion matrix.
    Optionally saves the confusion matrix as a PNG image.
    Returns the fitted model.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=y
    )

    print(f"\n[INFO] Training samples: {len(X_train)} | Test samples: {len(X_test)}")

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=None,
        random_state=RANDOM_SEED,
        class_weight="balanced"   # handles imbalanced approval/rejection ratios
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # ── Core metrics ───────────────────────────────────────────────────────
    accuracy  = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall    = recall_score(y_test, y_pred, zero_division=0)
    f1        = f1_score(y_test, y_pred, zero_division=0)

    print("\n" + "=" * 50)
    print("  EVALUATION METRICS")
    print("=" * 50)
    print(f"  Accuracy  : {accuracy:.4f}  ({accuracy * 100:.2f}%)")
    print(f"  Precision : {precision:.4f}")
    print(f"  Recall    : {recall:.4f}")
    print(f"  F1 Score  : {f1:.4f}")
    print("=" * 50)

    print("\n[RESULT] Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Rejected", "Approved"]))

    # ── Confusion matrix ────────────────────────────────────────────────────
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    print("[RESULT] Confusion Matrix (rows=Actual, cols=Predicted):")
    print(f"           Rejected  Approved")
    print(f"  Rejected   {cm[0][0]:>6}    {cm[0][1]:>6}")
    print(f"  Approved   {cm[1][0]:>6}    {cm[1][1]:>6}\n")

    if confusion_matrix_path:
        _save_confusion_matrix(cm, confusion_matrix_path)

    # ── Feature importances ─────────────────────────────────────────────────
    _print_feature_importances(model, CATEGORICAL_FEATURES + NUMERICAL_FEATURES)
    if feature_importance_path:
        _save_feature_importance_chart(
            model,
            CATEGORICAL_FEATURES + NUMERICAL_FEATURES,
            feature_importance_path,
        )

    return model


def _print_feature_importances(model, feature_names: list):
    """
    Extract feature_importances_ from the trained RandomForest and print
    a sorted table (descending) mapping each feature to its importance score.
    """
    importances = model.feature_importances_
    paired = sorted(
        zip(feature_names, importances),
        key=lambda x: x[1],
        reverse=True,
    )

    col_w = max(len(n) for n in feature_names) + 2
    print("\n" + "=" * 50)
    print("  FEATURE IMPORTANCES (descending)")
    print("=" * 50)
    print(f"  {'Feature':<{col_w}}  Importance")
    print(f"  {'-' * col_w}  ----------")
    for name, score in paired:
        bar = "█" * int(score * 40)          # visual bar, max 40 blocks
        print(f"  {name:<{col_w}}  {score:.4f}   {bar}")
    print("=" * 50 + "\n")


def _save_feature_importance_chart(model, feature_names: list, output_path: str):
    """
    Save a horizontal bar chart of feature importances as a PNG.
    Uses matplotlib with a non-interactive backend (Agg).
    Skips gracefully if matplotlib is not installed.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")   # non-interactive — no display required
        import matplotlib.pyplot as plt
        import numpy as np

        importances = model.feature_importances_
        indices = importances.argsort()          # ascending for horizontal bar
        sorted_names = [feature_names[i] for i in indices]
        sorted_scores = importances[indices]

        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.barh(sorted_names, sorted_scores, color="#667eea", edgecolor="white")
        ax.bar_label(bars, fmt="%.4f", padding=4, fontsize=9)
        ax.set_xlabel("Importance Score")
        ax.set_title("LoanMate — Feature Importances (RandomForest)")
        ax.set_xlim(0, max(sorted_scores) * 1.25)   # headroom for labels
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
        print(f"[INFO] Feature importance chart saved to: {output_path}")
    except ImportError:
        print("[WARNING] matplotlib not found — feature importance chart skipped.")
        print("          Install it with: pip install matplotlib")


def _save_confusion_matrix(cm, output_path: str):
    """
    Save the confusion matrix as a PNG image using scikit-learn's
    ConfusionMatrixDisplay. Requires matplotlib, which ships with
    scikit-learn's optional dependencies. Skips gracefully if unavailable.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")   # non-interactive backend — no display needed
        import matplotlib.pyplot as plt

        disp = ConfusionMatrixDisplay(
            confusion_matrix=cm,
            display_labels=["Rejected", "Approved"]
        )
        fig, ax = plt.subplots(figsize=(5, 4))
        disp.plot(ax=ax, colorbar=True, cmap="Blues")
        ax.set_title("LoanMate — Loan Decision Confusion Matrix")
        fig.tight_layout()
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
        print(f"[INFO] Confusion matrix image saved to: {output_path}")
    except ImportError:
        print("[WARNING] matplotlib not found — confusion matrix image skipped.")
        print("          Install it with: pip install matplotlib")


# ── Persistence ──────────────────────────────────────────────────────────────

def save_model(model, encoders: dict, model_path: str):
    """
    Save the trained model and fitted encoders together as a single artifact.
    Both are required at inference time.
    """
    artifact = {
        "model": model,
        "encoders": encoders,
        "feature_order": CATEGORICAL_FEATURES + NUMERICAL_FEATURES,
        "label_map": LABEL_MAP,
    }
    joblib.dump(artifact, model_path)
    print(f"\n[INFO] Model artifact saved to: {model_path}")


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="LoanMate ML Training Pipeline — decision-support only."
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Path to the exported loan decisions CSV file."
    )
    parser.add_argument(
        "--model",
        default="model.pkl",
        help="Output path for the trained model artifact (default: model.pkl)."
    )
    parser.add_argument(
        "--plot-cm",
        default=None,
        metavar="PATH",
        help="Optional: save the confusion matrix as a PNG image to this path."
    )
    parser.add_argument(
        "--plot-fi",
        default=None,
        metavar="PATH",
        help="Optional: save a feature importance bar chart as a PNG to this path."
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  LoanMate — Loan Eligibility Model Training")
    print("  NOTE: This model is decision-support ONLY.")
    print("        It does NOT automate or override officer decisions.")
    print("=" * 60)

    # Pipeline
    df = load_and_clean(args.data)
    X, y, encoders = encode_features(df)
    model = train_and_evaluate(
        X, y,
        confusion_matrix_path=args.plot_cm,
        feature_importance_path=args.plot_fi,
    )
    save_model(model, encoders, args.model)

    print("\n[DONE] Training complete.")


if __name__ == "__main__":
    main()
