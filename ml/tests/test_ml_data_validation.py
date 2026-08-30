import pytest
import pandas as pd
from ml.src.data_loader import generate_synthetic_benchmark_data
from ml.src.validation import validate_dataset_schema, compute_dataset_summary


def test_validate_dataset_schema_valid():
    df = generate_synthetic_benchmark_data(num_samples=30)
    is_valid, errors = validate_dataset_schema(df)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_dataset_schema_missing_column():
    df = generate_synthetic_benchmark_data(num_samples=30)
    df_missing = df.drop(columns=["dizziness_severity"])
    is_valid, errors = validate_dataset_schema(df_missing)
    assert is_valid is False
    assert any("dizziness_severity" in e for e in errors)


def test_validate_dataset_schema_impossible_values():
    df = generate_synthetic_benchmark_data(num_samples=30)
    df.loc[0, "dizziness_severity"] = 99.0  # Out of range > 10
    is_valid, errors = validate_dataset_schema(df)
    assert is_valid is False
    assert any("outside [0, 10]" in e for e in errors)


def test_compute_dataset_summary():
    df = generate_synthetic_benchmark_data(num_samples=30)
    summary = compute_dataset_summary(df)
    assert summary["total_records"] == 30
    assert "class_distribution" in summary
    assert summary["is_synthetic"] is True
