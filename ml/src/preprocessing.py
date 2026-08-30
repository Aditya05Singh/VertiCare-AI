from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.base import BaseEstimator, TransformerMixin

from ml.src.config import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    BOOLEAN_FEATURES,
    RISK_CLASSES
)

LABEL_MAP = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
INV_LABEL_MAP = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}


class BooleanTransformer(BaseEstimator, TransformerMixin):
    """Custom transformer to safely convert boolean and quasi-boolean values to binary integers (0 or 1)."""
    def fit(self, X, y=None):
        if hasattr(X, "shape"):
            self.n_features_in_ = X.shape[1]
        else:
            self.n_features_in_ = len(BOOLEAN_FEATURES)
        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            return X.fillna(False).astype(int).values
        arr = np.array(X)
        arr[pd.isna(arr)] = False
        return arr.astype(int)


def build_preprocessor() -> ColumnTransformer:
    """Builds a scikit-learn ColumnTransformer for numerical, categorical, and boolean features."""
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    bool_pipeline = Pipeline([
        ("bool_converter", BooleanTransformer()),
        ("imputer", SimpleImputer(strategy="most_frequent")),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, NUMERICAL_FEATURES),
            ("cat", cat_pipeline, CATEGORICAL_FEATURES),
            ("bool", bool_pipeline, BOOLEAN_FEATURES),
        ],
        remainder="drop"
    )

    return preprocessor


def encode_labels(labels: pd.Series) -> np.ndarray:
    """Encodes string target labels (LOW, MEDIUM, HIGH) to integers (0, 1, 2)."""
    return labels.map(LABEL_MAP).values


def decode_predictions(preds: np.ndarray) -> List[str]:
    """Decodes integer predictions back to string risk classes."""
    return [INV_LABEL_MAP.get(int(p), "MEDIUM") for p in preds]

