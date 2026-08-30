from typing import Tuple, List, Dict, Any
import pandas as pd
import numpy as np

from ml.src.config import (
    ALL_FEATURE_COLUMNS,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    BOOLEAN_FEATURES,
    TARGET_COLUMN,
    RISK_CLASSES
)

PROHIBITED_LEAKAGE_COLUMNS = {
    "patient_id", "user_id", "email", "password", "name",
    "first_name", "last_name", "phone", "token", "created_at"
}


def validate_dataset_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates dataset structure against schema specifications and checks for data leakage.
    """
    errors: List[str] = []

    if df.empty:
        return False, ["Dataset is empty."]

    # Check target column
    if TARGET_COLUMN not in df.columns:
        errors.append(f"Target column '{TARGET_COLUMN}' is missing.")
    else:
        unique_targets = set(df[TARGET_COLUMN].dropna().unique())
        invalid_targets = unique_targets - set(RISK_CLASSES)
        if invalid_targets:
            errors.append(f"Target column contains invalid classes: {invalid_targets}. Allowed: {RISK_CLASSES}")

    # Check required feature columns
    for col in ALL_FEATURE_COLUMNS:
        if col not in df.columns:
            errors.append(f"Required feature column '{col}' is missing from dataset.")

    # Check for prohibited leakage columns in feature set
    for col in df.columns:
        if col in PROHIBITED_LEAKAGE_COLUMNS and col in ALL_FEATURE_COLUMNS:
            errors.append(f"Data leakage risk: Prohibited identifier '{col}' found in feature set.")

    # Validate numerical boundaries
    if "dizziness_severity" in df.columns:
        if (df["dizziness_severity"] < 0).any() or (df["dizziness_severity"] > 10).any():
            errors.append("dizziness_severity contains values outside [0, 10] range.")

    if "imbalance_severity" in df.columns:
        if (df["imbalance_severity"] < 0).any() or (df["imbalance_severity"] > 10).any():
            errors.append("imbalance_severity contains values outside [0, 10] range.")

    if "sleep_hours" in df.columns:
        if (df["sleep_hours"] < 0).any() or (df["sleep_hours"] > 24).any():
            errors.append("sleep_hours contains impossible values outside [0, 24].")

    if "cv_valid_ratio" in df.columns:
        if (df["cv_valid_ratio"] < 0.0).any() or (df["cv_valid_ratio"] > 1.0).any():
            errors.append("cv_valid_ratio contains values outside [0.0, 1.0].")

    return (len(errors) == 0), errors


def compute_dataset_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generates technical summary of dataset balance, size, and missing value rates."""
    total_records = len(df)
    class_counts = df[TARGET_COLUMN].value_counts().to_dict() if TARGET_COLUMN in df.columns else {}
    missing_counts = df[ALL_FEATURE_COLUMNS].isnull().sum().to_dict() if set(ALL_FEATURE_COLUMNS).issubset(df.columns) else {}

    return {
        "total_records": total_records,
        "class_distribution": class_counts,
        "missing_values": missing_counts,
        "is_synthetic": "SYNTHETIC" in str(df.get("dataset_type", "")).upper() or "SYNTH" in str(df.get("patient_id", "")).upper()
    }

