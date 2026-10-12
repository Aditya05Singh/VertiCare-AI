"""
ml/src/general_symptom_engine/validation.py

Data validation, range checks, and leakage prevention for the General Symptom Engine.
"""

from typing import Tuple, List, Dict, Any, Union
import pandas as pd
import numpy as np

from ml.src.general_symptom_engine.config import (
    ALL_FEATURE_COLUMNS,
    BINARY_SYMPTOMS,
    NUMERICAL_DEMOGRAPHICS,
    CATEGORICAL_PROFILES,
    TARGET_COLUMN,
    TARGET_MAP,
    VALID_GENDERS,
    VALID_BP_LEVELS,
    VALID_CHOLESTEROL_LEVELS,
)

PROHIBITED_LEAKAGE_COLUMNS = {
    "patient_id", "user_id", "email", "name", "first_name", "last_name",
    "phone", "token", "ssn", "medical_record_number", "mrn"
}


def validate_training_dataset(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates training dataset schema, column presence, target labels, and leakage risks.
    """
    errors: List[str] = []

    if df.empty:
        return False, ["Dataset is empty."]

    # Check target
    if TARGET_COLUMN not in df.columns:
        errors.append(f"Target column '{TARGET_COLUMN}' is missing from dataset.")
    else:
        unrecognized_targets = set(df[TARGET_COLUMN].unique()) - set(TARGET_MAP.keys())
        if unrecognized_targets:
            errors.append(f"Target column contains unrecognized labels: {unrecognized_targets}")

    # Check required feature columns
    for col in ALL_FEATURE_COLUMNS:
        if col not in df.columns:
            errors.append(f"Required feature column '{col}' is missing.")

    # Leakage check: ensure identifiers are not in feature list
    for col in df.columns:
        if col.lower() in PROHIBITED_LEAKAGE_COLUMNS and col in ALL_FEATURE_COLUMNS:
            errors.append(f"Data leakage risk: prohibited identifier '{col}' found in feature set.")

    # Age sanity check
    if "Age" in df.columns:
        if (df["Age"] < 0).any() or (df["Age"] > 120).any():
            errors.append("Dataset contains Age values outside reasonable range [0, 120].")

    return (len(errors) == 0), errors


def validate_inference_input(record: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """
    Validates a single inference input payload.
    Returns:
        (is_valid, error_list, warning_list)
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(record, dict) or len(record) == 0:
        return False, ["Input record must be a non-empty dictionary."], warnings

    # Check for missing required features
    missing_features = [col for col in ALL_FEATURE_COLUMNS if col not in record]
    if missing_features:
        warnings.append(f"Missing features imputed with defaults: {missing_features}")

    # Age validation
    age = record.get("Age")
    if age is not None:
        try:
            age_f = float(age)
            if age_f < 0 or age_f > 120:
                errors.append(f"Age value ({age_f}) is outside valid physiological range [0, 120].")
        except (ValueError, TypeError):
            errors.append(f"Age value '{age}' cannot be converted to a numerical value.")

    # Gender validation
    gender = record.get("Gender")
    if gender is not None and str(gender).capitalize() not in VALID_GENDERS:
        warnings.append(f"Unrecognized gender '{gender}'. Will be treated as unknown category.")

    # Blood Pressure validation
    bp = record.get("Blood Pressure")
    if bp is not None and str(bp).capitalize() not in VALID_BP_LEVELS:
        warnings.append(f"Unrecognized blood pressure level '{bp}'. Allowed: {VALID_BP_LEVELS}")

    # Cholesterol Level validation
    chol = record.get("Cholesterol Level")
    if chol is not None and str(chol).capitalize() not in VALID_CHOLESTEROL_LEVELS:
        warnings.append(f"Unrecognized cholesterol level '{chol}'. Allowed: {VALID_CHOLESTEROL_LEVELS}")

    # Check for target column in input (leakage prevention)
    if TARGET_COLUMN in record:
        warnings.append(f"Target column '{TARGET_COLUMN}' found in inference input and will be ignored.")

    return (len(errors) == 0), errors, warnings

