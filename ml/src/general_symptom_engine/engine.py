"""
ml/src/general_symptom_engine/engine.py

Standalone reusable interface for the Experimental General-Symptom Engine.
Provides schema validation, cached inference, warnings, and limitations.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
import joblib
import pandas as pd
import numpy as np

from ml.src.general_symptom_engine.config import (
    MODEL_PATH,
    METADATA_PATH,
    ALL_FEATURE_COLUMNS,
    BINARY_SYMPTOMS,
    MODEL_VERSION,
    MODEL_NAME,
    ASSESSMENT_TYPE,
)
from ml.src.general_symptom_engine.validation import validate_inference_input
from ml.src.general_symptom_engine.preprocessing import decode_target


@dataclass
class GeneralSymptomAssessmentResult:
    """Structured assessment result returned by the General Symptom Engine."""
    assessment_type: str
    model_version: str
    status: str
    prediction: Optional[str]
    probability_positive: Optional[float]
    confidence_tier: str
    data_quality_warnings: List[str] = field(default_factory=list)
    insufficient_information: bool = False
    relevant_limitations: List[str] = field(default_factory=list)
    contributing_symptoms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_type": self.assessment_type,
            "model_version": self.model_version,
            "status": self.status,
            "prediction": self.prediction,
            "probability_positive": self.probability_positive,
            "confidence_tier": self.confidence_tier,
            "data_quality_warnings": self.data_quality_warnings,
            "insufficient_information": self.insufficient_information,
            "relevant_limitations": self.relevant_limitations,
            "contributing_symptoms": self.contributing_symptoms,
        }


class GeneralSymptomRiskEngine:
    """
    Reusable inference engine for general symptom profile assessment.
    """
    _pipeline = None
    _metadata: Optional[Dict[str, Any]] = None

    STANDARD_LIMITATIONS: List[str] = [
        "Dataset provenance: Kaggle Disease Symptoms and Patient Profile Dataset (349 records).",
        "This engine assesses general illness symptom patterns and DOES NOT evaluate vertigo, BPPV, or vestibular disorders.",
        "Prototype model for software verification and algorithmic benchmarking only. Not a medical diagnostic tool."
    ]

    @classmethod
    def load_model(cls, force_reload: bool = False) -> Any:
        """Loads and caches the trained pipeline from disk."""
        if cls._pipeline is None or force_reload:
            if not MODEL_PATH.exists():
                return None
            cls._pipeline = joblib.load(MODEL_PATH)

            if METADATA_PATH.exists():
                try:
                    with open(METADATA_PATH, "r") as f:
                        cls._metadata = json.load(f)
                except Exception:
                    cls._metadata = None
        return cls._pipeline

    @classmethod
    def assess(cls, patient_profile: Dict[str, Any]) -> GeneralSymptomAssessmentResult:
        """
        Assesses a patient symptom profile.
        Validates input, checks model availability, handles edge cases,
        and returns a structured GeneralSymptomAssessmentResult.
        """
        # 1. Input Validation
        is_valid, errors, warnings = validate_inference_input(patient_profile)
        if not is_valid:
            return GeneralSymptomAssessmentResult(
                assessment_type=ASSESSMENT_TYPE,
                model_version=MODEL_VERSION,
                status="INVALID_INPUT",
                prediction=None,
                probability_positive=None,
                confidence_tier="NONE",
                data_quality_warnings=errors + warnings,
                insufficient_information=True,
                relevant_limitations=cls.STANDARD_LIMITATIONS
            )

        # 2. Insufficient Information Check
        # If all symptoms are missing or none provided
        symptoms_present = [s for s in BINARY_SYMPTOMS if s in patient_profile and patient_profile[s] not in (None, "")]
        if len(symptoms_present) == 0 and "Age" not in patient_profile:
            return GeneralSymptomAssessmentResult(
                assessment_type=ASSESSMENT_TYPE,
                model_version=MODEL_VERSION,
                status="INSUFFICIENT_INFORMATION",
                prediction=None,
                probability_positive=None,
                confidence_tier="NONE",
                data_quality_warnings=warnings + ["No symptoms or demographic indicators were provided."],
                insufficient_information=True,
                relevant_limitations=cls.STANDARD_LIMITATIONS
            )

        # 3. Model Availability Check
        pipeline = cls.load_model()
        if pipeline is None:
            return GeneralSymptomAssessmentResult(
                assessment_type=ASSESSMENT_TYPE,
                model_version=MODEL_VERSION,
                status="MODEL_UNAVAILABLE",
                prediction=None,
                probability_positive=None,
                confidence_tier="NONE",
                data_quality_warnings=warnings + [f"Trained model artifact not found at {MODEL_PATH}."],
                insufficient_information=True,
                relevant_limitations=cls.STANDARD_LIMITATIONS
            )

        # 4. Construct feature DataFrame with canonical columns
        row_data: Dict[str, Any] = {}
        contributing: List[str] = []

        for col in ALL_FEATURE_COLUMNS:
            val = patient_profile.get(col)
            if col in BINARY_SYMPTOMS:
                val_str = str(val).strip().capitalize() if val is not None else "No"
                row_data[col] = val_str
                if val_str in ("Yes", "True", "1"):
                    contributing.append(col)
            elif col == "Age":
                row_data[col] = float(val) if val is not None else 40.0
            else:
                row_data[col] = str(val).strip().capitalize() if val is not None else "Normal"

        df_input = pd.DataFrame([row_data], columns=ALL_FEATURE_COLUMNS)

        # 5. Execute Prediction
        pred_int = int(pipeline.predict(df_input)[0])
        pred_label = decode_target(np.array([pred_int]))[0]

        prob_pos = None
        confidence = "MODERATE"

        if hasattr(pipeline, "predict_proba"):
            probas = pipeline.predict_proba(df_input)[0]
            if len(probas) == 2:
                prob_pos = round(float(probas[1]), 4)
                # Assign confidence tier based on distance from decision threshold (0.5)
                dist = abs(prob_pos - 0.5)
                if dist >= 0.30:
                    confidence = "HIGH"
                elif dist >= 0.15:
                    confidence = "MODERATE"
                else:
                    confidence = "LOW"

        return GeneralSymptomAssessmentResult(
            assessment_type=ASSESSMENT_TYPE,
            model_version=MODEL_VERSION,
            status="COMPLETED",
            prediction=pred_label,
            probability_positive=prob_pos,
            confidence_tier=confidence,
            data_quality_warnings=warnings,
            insufficient_information=False,
            relevant_limitations=cls.STANDARD_LIMITATIONS,
            contributing_symptoms=contributing
        )

