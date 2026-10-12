"""
ml/src/general_symptom_engine/train.py

Model training, multi-model evaluation, serialization, and report generation
for the Experimental General-Symptom Engine.
"""

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from ml.src.general_symptom_engine.config import (
    RAW_DATA_PATH,
    MODEL_PATH,
    METADATA_PATH,
    REPORT_PATH,
    MODELS_DIR,
    REPORTS_DIR,
    MODEL_VERSION,
    MODEL_NAME,
    ASSESSMENT_TYPE,
    ALL_FEATURE_COLUMNS,
    TARGET_COLUMN,
    RANDOM_STATE,
)
from ml.src.general_symptom_engine.data_loader import load_dataset, inspect_dataset_properties
from ml.src.general_symptom_engine.validation import validate_training_dataset
from ml.src.general_symptom_engine.preprocessing import (
    build_preprocessor,
    encode_target,
)
from ml.src.general_symptom_engine.evaluate import compute_binary_metrics


def get_candidate_models() -> Dict[str, Any]:
    """Returns baseline and candidate models for comparison."""
    return {
        "DummyBaseline": DummyClassifier(strategy="most_frequent", random_state=RANDOM_STATE),
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=RANDOM_STATE),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=80, max_depth=3, learning_rate=0.1, random_state=RANDOM_STATE),
    }


def train_and_compare_models(csv_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Executes end-to-end model training, cross-validation, holdout evaluation,
    artifact persistence, and detailed performance reporting.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Ingest and Validate Dataset
    df = load_dataset(csv_path)
    is_valid, validation_errors = validate_training_dataset(df)
    if not is_valid:
        raise ValueError(f"Dataset validation failed: {validation_errors}")

    dataset_summary = inspect_dataset_properties(df)

    X = df[ALL_FEATURE_COLUMNS].copy()
    y = encode_target(df[TARGET_COLUMN])

    # 2. Stratified Train / Test Holdout Split (75% Train, 25% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    candidates = get_candidate_models()
    comparison_results: Dict[str, Any] = {}
    best_model_name = "LogisticRegression"
    best_f1 = -1.0
    best_fitted_pipeline: Optional[Pipeline] = None

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    # 3. Fit and evaluate each candidate
    for name, model in candidates.items():
        preprocessor = build_preprocessor()
        full_pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", model)
        ])

        # 5-Fold Stratified Cross Validation on train set
        cv_scores = cross_val_score(full_pipeline, X_train, y_train, cv=cv, scoring="f1_macro")
        mean_cv_f1 = float(np.mean(cv_scores))

        # Fit on entire training set
        full_pipeline.fit(X_train, y_train)

        # Predict on held-out test set
        y_test_pred = full_pipeline.predict(X_test)
        y_test_proba = full_pipeline.predict_proba(X_test) if hasattr(full_pipeline, "predict_proba") else None

        metrics = compute_binary_metrics(y_test, y_test_pred, y_test_proba)
        metrics["cv_f1_macro_mean"] = round(mean_cv_f1, 4)
        comparison_results[name] = metrics

        # Select best trained model (excluding trivial dummy baseline) based on holdout macro F1
        if name != "DummyBaseline" and metrics["f1_macro"] > best_f1:
            best_f1 = metrics["f1_macro"]
            best_model_name = name
            best_fitted_pipeline = full_pipeline

    if best_fitted_pipeline is None:
        raise RuntimeError("Failed to fit any candidate model.")

    # 4. Serialize Best Model Pipeline
    joblib.dump(best_fitted_pipeline, MODEL_PATH)

    # 5. Metadata Schema
    metadata = {
        "model_name": best_model_name,
        "model_version": MODEL_VERSION,
        "assessment_type": ASSESSMENT_TYPE,
        "trained_timestamp": datetime.now(timezone.utc).isoformat(),
        "random_state": RANDOM_STATE,
        "dataset_inspection": dataset_summary,
        "dataset_split": {
            "total_records": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        },
        "feature_names": ALL_FEATURE_COLUMNS,
        "selected_model_metrics": comparison_results[best_model_name],
        "provenance_notice": (
            "Trained on Kaggle Disease Symptoms and Patient Profile Dataset (349 records). "
            "Contains general illness labels only (e.g., Asthma, Stroke, Influenza). "
            "Does not contain vertigo, BPPV, or vestibular disorder labels. "
            "Experimental prototype only; not a clinically validated diagnostic tool."
        )
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    # 6. Evaluation Summary Report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "assessment_type": ASSESSMENT_TYPE,
        "selected_model": best_model_name,
        "selection_criteria": "Highest holdout F1-score with balanced generalization",
        "model_comparisons": comparison_results,
        "limitations": [
            "Dataset is a limited 349-row toy/demonstration cohort.",
            "High metric scores reflect small-sample characteristics, not generalizable clinical validity.",
            "Zero vestibular or vertigo-specific diagnoses in training data."
        ]
    }

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    rep = train_and_compare_models()
    print("Training finished. Selected Model:", rep["selected_model"])
    print(json.dumps(rep, indent=2))
