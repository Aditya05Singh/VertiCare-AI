"""
ml/src/general_symptom_engine/preprocessing.py

Feature encoding pipelines and transformers for general symptom classification.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

from ml.src.general_symptom_engine.config import (
    BINARY_SYMPTOMS,
    NUMERICAL_DEMOGRAPHICS,
    CATEGORICAL_PROFILES,
    TARGET_MAP,
    INV_TARGET_MAP,
)


class BinarySymptomTransformer(BaseEstimator, TransformerMixin):
    """
    Safely converts Yes/No string indicators, booleans, or numerical flags into binary integers (0 or 1).
    """

    def fit(self, X, y=None):
        if hasattr(X, "shape"):
            self.n_features_in_ = X.shape[1]
        else:
            self.n_features_in_ = len(BINARY_SYMPTOMS)
        return self

    def transform(self, X):
        df_x = pd.DataFrame(X).copy()
        for col in df_x.columns:
            df_x[col] = df_x[col].apply(self._convert_to_binary)
        return df_x.values.astype(np.float64)

    @staticmethod
    def _convert_to_binary(val: Any) -> int:
        if pd.isna(val) or val is None:
            return 0
        s = str(val).strip().lower()
        if s in ("yes", "y", "true", "1", "present", "positive"):
            return 1
        return 0


def build_preprocessor() -> ColumnTransformer:
    """
    Constructs a ColumnTransformer that encodes binary symptoms, standardizes continuous age,
    and one-hot encodes patient categorical profiles with out-of-vocabulary unknown category handling.
    """
    binary_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="No")),
        ("binarizer", BinarySymptomTransformer()),
    ])

    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("binary", binary_pipeline, BINARY_SYMPTOMS),
            ("num", num_pipeline, NUMERICAL_DEMOGRAPHICS),
            ("cat", cat_pipeline, CATEGORICAL_PROFILES),
        ],
        remainder="drop"
    )
    return preprocessor


def encode_target(y_series: pd.Series) -> np.ndarray:
    """Encode string targets ('Positive', 'Negative') to integer binary array (1, 0)."""
    return y_series.map(TARGET_MAP).fillna(0).astype(int).values


def decode_target(y_preds: np.ndarray) -> List[str]:
    """Decode integer predictions back to string outcome labels."""
    return [INV_TARGET_MAP.get(int(p), "Negative") for p in y_preds]

