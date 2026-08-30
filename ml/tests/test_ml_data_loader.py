import pytest
from ml.src.data_loader import generate_synthetic_benchmark_data
from ml.src.config import ALL_FEATURE_COLUMNS, TARGET_COLUMN


def test_generate_synthetic_benchmark_data():
    df = generate_synthetic_benchmark_data(num_samples=50)
    assert len(df) == 50
    assert TARGET_COLUMN in df.columns
    for col in ALL_FEATURE_COLUMNS:
        assert col in df.columns
    assert set(df[TARGET_COLUMN].unique()).issubset({"LOW", "MEDIUM", "HIGH"})
