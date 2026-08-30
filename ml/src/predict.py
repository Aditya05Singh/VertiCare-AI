import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import joblib
import pandas as pd
import numpy as np

from ml.src.config import (
    MODEL_PATH,
    METADATA_PATH,
    ALL_FEATURE_COLUMNS,
    MODEL_NAME,
    MODEL_VERSION,
    RISK_CLASSES,
)
from ml.src.preprocessing import decode_predictions
from ml.src.feature_engineering import identify_contributing_factors


class RiskPredictor:
    """
    Cached ML prediction service for evaluating vestibular screening risk level.
    """
    _pipeline = None
    _metadata = None

    @classmethod
    def load_model(cls, force_reload: bool = False) -> Any:
        """Loads and caches the trained scikit-learn/xgboost pipeline."""
        if cls._pipeline is None or force_reload:
            if not os.path.exists(MODEL_PATH):
                return None
            cls._pipeline = joblib.load(MODEL_PATH)

            if os.path.exists(METADATA_PATH):
                with open(METADATA_PATH, "r") as f:
                    cls._metadata = json.load(f)
            else:
                cls._metadata = {"model_name": MODEL_NAME, "model_version": MODEL_VERSION}

        return cls._pipeline

    @classmethod
    def predict(cls, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes inference on a multimodal feature dictionary.
        Returns risk_level (LOW, MEDIUM, HIGH), continuous risk_score, class probabilities,
        and explainable contributing factors.
        """
        pipeline = cls.load_model()
        if pipeline is None:
            raise RuntimeError("Trained ML risk model artifact is not available on disk.")

        # Construct single-row DataFrame with explicit column order
        row_dict = {col: feature_dict.get(col, 0.0) for col in ALL_FEATURE_COLUMNS}
        input_df = pd.DataFrame([row_dict], columns=ALL_FEATURE_COLUMNS)

        pred_int = int(pipeline.predict(input_df)[0])
        risk_level = decode_predictions([pred_int])[0]

        # Calculate calibrated risk score from class probabilities if available
        risk_score = 0.5
        prob_dict = {}
        if hasattr(pipeline, "predict_proba"):
            probas = pipeline.predict_proba(input_df)[0]
            for idx, cls_name in enumerate(RISK_CLASSES):
                if idx < len(probas):
                    prob_dict[cls_name] = round(float(probas[idx]), 4)

            # Continuous severity risk score [0.0 - 1.0]
            # Low center 0.15, Medium center 0.50, High center 0.90
            p_low = prob_dict.get("LOW", 0.0)
            p_med = prob_dict.get("MEDIUM", 0.0)
            p_high = prob_dict.get("HIGH", 0.0)
            risk_score = round(float(p_low * 0.15 + p_med * 0.50 + p_high * 0.90), 3)

        contributing_factors = identify_contributing_factors(feature_dict)

        model_name = cls._metadata.get("model_name", MODEL_NAME) if cls._metadata else MODEL_NAME
        model_ver = cls._metadata.get("model_version", MODEL_VERSION) if cls._metadata else MODEL_VERSION

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "probabilities": prob_dict,
            "model_name": model_name,
            "model_version": model_ver,
            "contributing_factors": contributing_factors,
            "notice": "AI-assisted screening estimate for clinical decision support. Not a medical diagnosis."
        }

