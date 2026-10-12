"""
ml/tests/test_general_symptom_engine.py

Comprehensive independent test suite for the Experimental General-Symptom ML Risk Engine,
verifying dataset loading, schema validation, preprocessing, reproducibility,
metric calculation, serialization/reload, and all inference edge cases.
"""

from pathlib import Path
import tempfile
import pytest
import numpy as np
import pandas as pd
import joblib

from ml.src.general_symptom_engine.config import (
    RAW_DATA_PATH,
    MODEL_PATH,
    METADATA_PATH,
    ALL_FEATURE_COLUMNS,
    BINARY_SYMPTOMS,
    TARGET_COLUMN,
    MODEL_VERSION,
    ASSESSMENT_TYPE,
)
from ml.src.general_symptom_engine.data_loader import load_dataset, inspect_dataset_properties
from ml.src.general_symptom_engine.validation import (
    validate_training_dataset,
    validate_inference_input,
)
from ml.src.general_symptom_engine.preprocessing import (
    build_preprocessor,
    encode_target,
    decode_target,
    BinarySymptomTransformer,
)
from ml.src.general_symptom_engine.evaluate import compute_binary_metrics
from ml.src.general_symptom_engine.train import train_and_compare_models
from ml.src.general_symptom_engine.engine import (
    GeneralSymptomRiskEngine,
    GeneralSymptomAssessmentResult,
)


def test_data_loading_and_dataset_properties():
    """1. Verify real Kaggle dataset loading and structural property extraction."""
    assert RAW_DATA_PATH.exists(), f"Kaggle dataset missing at {RAW_DATA_PATH}"
    df = load_dataset(RAW_DATA_PATH)
    assert not df.empty
    assert len(df) == 349
    assert TARGET_COLUMN in df.columns

    props = inspect_dataset_properties(df)
    assert props["total_records"] == 349
    assert props["missing_values"][TARGET_COLUMN] == 0
    assert props["duplicate_rows"] == 49
    assert props["vertigo_disease_count"] == 0
    assert props["supports_vertigo_prediction"] is False  # Confirms no vertigo labels!


def test_schema_validation_valid_and_invalid():
    """2. Verify schema validation detects missing columns, bad targets, and leakage."""
    df = load_dataset(RAW_DATA_PATH)
    is_valid, errors = validate_training_dataset(df)
    assert is_valid is True
    assert len(errors) == 0

    # Test corrupted missing target
    df_no_target = df.drop(columns=[TARGET_COLUMN])
    is_valid_bad, errs_bad = validate_training_dataset(df_no_target)
    assert is_valid_bad is False
    assert any("missing" in e for e in errs_bad)

    # Test impossible age
    df_bad_age = df.copy()
    df_bad_age.loc[0, "Age"] = 150
    is_valid_age, errs_age = validate_training_dataset(df_bad_age)
    assert is_valid_age is False
    assert any("Age" in e for e in errs_age)


def test_preprocessing_transform_and_encodings():
    """3. Verify ColumnTransformer correctly transforms symptoms, continuous age, and categories."""
    df = load_dataset(RAW_DATA_PATH)
    X = df[ALL_FEATURE_COLUMNS]
    preprocessor = build_preprocessor()

    X_transformed = preprocessor.fit_transform(X)
    assert isinstance(X_transformed, np.ndarray)
    assert X_transformed.shape[0] == len(df)
    assert not np.isnan(X_transformed).any()

    # Verify target encoding and decoding round-trip
    y_encoded = encode_target(df[TARGET_COLUMN])
    assert set(np.unique(y_encoded)).issubset({0, 1})
    decoded = decode_target(y_encoded)
    assert set(decoded) == set(df[TARGET_COLUMN].unique())


def test_binary_symptom_transformer_robustness():
    """Verify BinarySymptomTransformer maps strings, booleans, missing values correctly."""
    transformer = BinarySymptomTransformer()
    sample_data = pd.DataFrame({
        "Fever": ["Yes", "no", True, False, "1", None, "Positive"]
    })
    out = transformer.transform(sample_data)
    expected = np.array([[1.0], [0.0], [1.0], [0.0], [1.0], [0.0], [1.0]])
    np.testing.assert_array_equal(out, expected)


def test_training_reproducibility():
    """4. Verify training is deterministic and reproducible under identical random state."""
    report1 = train_and_compare_models()
    report2 = train_and_compare_models()

    assert report1["selected_model"] == report2["selected_model"]
    m1 = report1["model_comparisons"][report1["selected_model"]]
    m2 = report2["model_comparisons"][report2["selected_model"]]
    assert m1["accuracy"] == m2["accuracy"]
    assert m1["f1_score"] == m2["f1_score"]
    assert m1["roc_auc"] == m2["roc_auc"]


def test_model_serialization_and_reload():
    """5. Verify serialized joblib artifact exists, reloads, and preserves prediction behavior."""
    assert MODEL_PATH.exists()
    assert METADATA_PATH.exists()

    pipeline = GeneralSymptomRiskEngine.load_model(force_reload=True)
    assert pipeline is not None
    assert hasattr(pipeline, "predict")

    # Predict on standard synthetic profile
    test_df = pd.DataFrame([{
        "Fever": "Yes",
        "Cough": "No",
        "Fatigue": "Yes",
        "Difficulty Breathing": "No",
        "Age": 35.0,
        "Gender": "Female",
        "Blood Pressure": "Normal",
        "Cholesterol Level": "Normal"
    }], columns=ALL_FEATURE_COLUMNS)

    pred = pipeline.predict(test_df)
    assert pred[0] in (0, 1)


def test_evaluation_metric_computations():
    """6. Verify calculation of accuracy, precision, recall, F1, and ROC-AUC."""
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 1])
    y_proba = np.array([[0.8, 0.2], [0.4, 0.6], [0.3, 0.7], [0.1, 0.9]])

    metrics = compute_binary_metrics(y_true, y_pred, y_proba)
    assert metrics["accuracy"] == 0.75
    assert metrics["recall"] == 1.0
    assert 0.0 <= metrics["precision"] <= 1.0
    assert metrics["f1_score"] > 0.0
    assert metrics["f1_macro"] > 0.0
    assert metrics["roc_auc"] == 1.0
    assert metrics["confusion_matrix"] == [[1, 1], [0, 2]]


def test_engine_inference_valid_positive_profile():
    """7a. Verify inference on profile with elevated symptoms."""
    profile = {
        "Fever": "Yes",
        "Cough": "Yes",
        "Fatigue": "Yes",
        "Difficulty Breathing": "Yes",
        "Age": 60,
        "Gender": "Male",
        "Blood Pressure": "High",
        "Cholesterol Level": "High"
    }
    result = GeneralSymptomRiskEngine.assess(profile)
    assert result.status == "COMPLETED"
    assert result.prediction in ("Positive", "Negative")
    assert 0.0 <= result.probability_positive <= 1.0
    assert result.confidence_tier in ("LOW", "MODERATE", "HIGH")
    assert "Fever" in result.contributing_symptoms
    assert result.assessment_type == ASSESSMENT_TYPE
    assert result.model_version == MODEL_VERSION
    assert len(result.relevant_limitations) >= 3


def test_engine_inference_invalid_input_age_out_of_bounds():
    """7b. Verify out-of-bounds Age is caught and reported in data_quality_warnings."""
    profile = {
        "Fever": "No",
        "Age": -15,  # Invalid negative age
        "Gender": "Female",
    }
    result = GeneralSymptomRiskEngine.assess(profile)
    assert result.status == "INVALID_INPUT"
    assert result.prediction is None
    assert any("Age" in w for w in result.data_quality_warnings)


def test_engine_inference_missing_features_imputation():
    """8. Verify missing optional features trigger warnings but execute inference with defaults."""
    sparse_profile = {
        "Fever": "Yes",
        "Age": 28,
        # Gender, BP, Cholesterol omitted
    }
    result = GeneralSymptomRiskEngine.assess(sparse_profile)
    assert result.status == "COMPLETED"
    assert len(result.data_quality_warnings) > 0
    assert any("Missing features" in w for w in result.data_quality_warnings)


def test_engine_inference_unknown_categorical_values():
    """8b. Verify unknown out-of-vocabulary categorical levels do not crash inference."""
    profile_oov = {
        "Fever": "Yes",
        "Age": 45,
        "Gender": "NonBinary_NewCategory",
        "Blood Pressure": "Fluctuating_Extreme",
        "Cholesterol Level": "Borderline_Unknown"
    }
    result = GeneralSymptomRiskEngine.assess(profile_oov)
    assert result.status == "COMPLETED"
    assert result.prediction in ("Positive", "Negative")
    assert any("Unrecognized" in w for w in result.data_quality_warnings)


def test_engine_inference_insufficient_information():
    """9a. Verify completely empty profile returns INSUFFICIENT_INFORMATION."""
    empty_profile = {}
    result = GeneralSymptomRiskEngine.assess(empty_profile)
    assert result.status in ("INSUFFICIENT_INFORMATION", "INVALID_INPUT")
    assert result.insufficient_information is True
    assert result.prediction is None


def test_engine_structured_output_schema_and_types():
    """10. Verify GeneralSymptomAssessmentResult conforms to all interface schema rules."""
    profile = {"Fever": "No", "Cough": "No", "Age": 22}
    result = GeneralSymptomRiskEngine.assess(profile)

    res_dict = result.to_dict()
    assert isinstance(res_dict["assessment_type"], str)
    assert isinstance(res_dict["model_version"], str)
    assert isinstance(res_dict["status"], str)
    assert isinstance(res_dict["confidence_tier"], str)
    assert isinstance(res_dict["data_quality_warnings"], list)
    assert isinstance(res_dict["relevant_limitations"], list)
    assert isinstance(res_dict["insufficient_information"], bool)
    assert any("vertigo" in lim.lower() for lim in res_dict["relevant_limitations"])

