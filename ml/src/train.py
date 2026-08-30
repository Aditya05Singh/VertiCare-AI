import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from ml.src.config import (
    ALL_FEATURE_COLUMNS,
    TARGET_COLUMN,
    RANDOM_STATE,
    MODEL_PATH,
    METADATA_PATH,
    REPORT_PATH,
    MODELS_DIR,
    REPORTS_DIR,
    MODEL_VERSION,
)
from ml.src.data_loader import load_raw_dataset
from ml.src.validation import validate_dataset_schema
from ml.src.preprocessing import build_preprocessor, encode_labels, decode_predictions
from ml.src.evaluate import compute_classification_metrics


def get_candidate_models() -> Dict[str, Any]:
    """Returns candidate classification algorithms, safely adapting to available environment runtimes."""
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=6, random_state=RANDOM_STATE),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=RANDOM_STATE)
    }

    try:
        from xgboost import XGBClassifier
        models["XGBoost"] = XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.08,
            eval_metric="mlogloss",
            random_state=RANDOM_STATE
        )
    except Exception:
        # If OpenMP / libomp is not installed on macOS, GradientBoosting serves as the boosted tree comparator
        pass

    return models


def train_and_compare_models(csv_path: Path = None) -> Dict[str, Any]:
    """
    Orchestrates dataset loading, validation, preprocessing, multi-model comparison,
    best-model selection, artifact persistence, and evaluation report generation.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # 1. Load and Validate Dataset
    df = load_raw_dataset(csv_path)
    is_valid, validation_errors = validate_dataset_schema(df)
    if not is_valid:
        raise ValueError(f"Dataset validation failed: {validation_errors}")

    X = df[ALL_FEATURE_COLUMNS].copy()
    y = encode_labels(df[TARGET_COLUMN])

    # 2. Stratified Train / Test Split (80% Train, 20% Holdout Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    # 3. Define and Evaluate Candidate Models
    candidates = get_candidate_models()

    comparison_results: Dict[str, Any] = {}
    best_model_name = "RandomForest"
    best_f1 = -1.0
    best_fitted_pipeline = None

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    for name, model in candidates.items():
        preprocessor = build_preprocessor()
        full_pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", model)
        ])

        # 5-Fold Stratified Cross-Validation on training set
        cv_scores = cross_val_score(full_pipeline, X_train, y_train, cv=cv, scoring="f1_macro")
        mean_cv_f1 = float(np.mean(cv_scores))

        # Fit on entire training set and evaluate on test set
        full_pipeline.fit(X_train, y_train)
        y_test_pred = full_pipeline.predict(X_test)
        y_test_proba = full_pipeline.predict_proba(X_test) if hasattr(full_pipeline, "predict_proba") else None

        test_metrics = compute_classification_metrics(y_test, y_test_pred, y_test_proba)
        test_metrics["cv_f1_macro_mean"] = round(mean_cv_f1, 4)

        comparison_results[name] = test_metrics

        if mean_cv_f1 > best_f1:
            best_f1 = mean_cv_f1
            best_model_name = name
            best_fitted_pipeline = full_pipeline

    # 4. Save Best Pipeline Artifact
    joblib.dump(best_fitted_pipeline, MODEL_PATH)

    # 5. Metadata Schema
    metadata = {
        "model_name": best_model_name,
        "model_version": MODEL_VERSION,
        "training_date": datetime.now(timezone.utc).isoformat(),
        "random_state": RANDOM_STATE,
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_names": ALL_FEATURE_COLUMNS,
        "selected_model_metrics": comparison_results[best_model_name],
        "dataset_reference": "synthetic_benchmark_demo_dataset",
        "notice": "Trained for software prototype verification. Not a clinically validated diagnostic tool."
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    # 6. Save Comparison Summary Report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "selected_model": best_model_name,
        "selection_reason": f"Highest 5-Fold Cross-Validation Macro F1 Score ({round(best_f1, 4)}) with balanced generalization across risk tiers.",
        "model_comparisons": comparison_results
    }

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    report = train_and_compare_models()
    print("Training Complete. Selected Model:", report["selected_model"])
    print(json.dumps(report, indent=2))

