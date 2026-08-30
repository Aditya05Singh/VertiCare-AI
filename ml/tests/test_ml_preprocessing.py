import pytest
import pandas as pd
import numpy as np
from ml.src.data_loader import generate_synthetic_benchmark_data
from ml.src.preprocessing import build_preprocessor, encode_labels, decode_predictions
from ml.src.config import ALL_FEATURE_COLUMNS


def test_build_preprocessor_transform():
    df = generate_synthetic_benchmark_data(num_samples=40)
    X = df[ALL_FEATURE_COLUMNS]

    preprocessor = build_preprocessor()
    X_trans = preprocessor.fit_transform(X)

    assert X_trans.shape[0] == 40
    assert not np.isnan(X_trans).any()


def test_label_encoding_and_decoding():
    labels = pd.Series(["LOW", "MEDIUM", "HIGH", "LOW"])
    encoded = encode_labels(labels)
    assert list(encoded) == [0, 1, 2, 0]

    decoded = decode_predictions(encoded)
    assert list(decoded) == ["LOW", "MEDIUM", "HIGH", "LOW"]
