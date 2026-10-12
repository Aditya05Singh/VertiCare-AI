"""
ml/src/general_symptom_engine/data_loader.py

Data ingestion and structural inspection for the Kaggle Disease Symptoms and Patient Profile Dataset.
"""

from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np

from ml.src.general_symptom_engine.config import (
    RAW_DATA_PATH,
    TARGET_COLUMN,
    DISEASE_NAME_COLUMN,
    ALL_FEATURE_COLUMNS,
)


def load_dataset(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Loads and cleans string whitespace from the Disease Symptoms and Patient Profile dataset.
    Raises FileNotFoundError if file is missing.
    """
    path = Path(csv_path or RAW_DATA_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Kaggle dataset file not found at: {path}")

    df = pd.read_csv(path)
    # Strip whitespace from column headers
    df.columns = df.columns.str.strip()

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object", "string", "str"]).columns:
        df[col] = df[col].astype(str).str.strip()

    return df


def inspect_dataset_properties(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Inspects and audits structural properties, target labels, missing values,
    duplicates, class balance, and checks for vertigo/vestibular targets.
    """
    total_rows, total_cols = df.shape
    missing_dict = df.isnull().sum().to_dict()
    duplicate_count = int(df.duplicated().sum())

    target_dist = df[TARGET_COLUMN].value_counts().to_dict() if TARGET_COLUMN in df.columns else {}
    unique_diseases = int(df[DISEASE_NAME_COLUMN].nunique()) if DISEASE_NAME_COLUMN in df.columns else 0

    # Search for any vertigo, vestibular, or balance-related disease labels
    vertigo_count = 0
    if DISEASE_NAME_COLUMN in df.columns:
        vertigo_mask = df[DISEASE_NAME_COLUMN].str.contains(
            r"vertigo|vestibular|meniere|bppv|labyrinthitis|dizzy|dizziness",
            case=False,
            na=False
        )
        vertigo_count = int(vertigo_mask.sum())

    return {
        "total_records": total_rows,
        "total_columns": total_cols,
        "columns": list(df.columns),
        "target_distribution": target_dist,
        "missing_values": missing_dict,
        "duplicate_rows": duplicate_count,
        "unique_disease_count": unique_diseases,
        "vertigo_disease_count": vertigo_count,
        "supports_vertigo_prediction": (vertigo_count > 0),
        "dataset_provenance": "Kaggle (uom190346a) - 349 general illness symptom profiles"
    }
