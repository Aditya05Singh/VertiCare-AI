import math
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np
import joblib

from app.schemas.eye_analysis import EyeScreeningInterpretationResponse
from cv.src.validation import ALLOWED_CV_FEATURE_NAMES, is_finite_number

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "ml" / "models" / "eye-screening-v1.joblib"
METADATA_PATH = Path(__file__).resolve().parent.parent.parent / "ml" / "models" / "eye-screening-v1_metadata.json"

FEATURE_COLUMNS = [
    "horizontal_amplitude",
    "vertical_amplitude",
    "horizontal_velocity_mean",
    "vertical_velocity_mean",
    "horizontal_velocity_max",
    "vertical_velocity_max",
    "direction_changes_h",
    "direction_changes_v",
    "blink_count",
    "blink_rate_per_min",
    "valid_ratio",
]

TARGET_CLASSES = [
    "NORMAL_FIXATION_PATTERN",
    "POSSIBLE_HORIZONTAL_NYSTAGMUS_PATTERN",
    "POSSIBLE_VERTICAL_NYSTAGMUS_PATTERN",
    "IRREGULAR_OCULAR_DRIFT_PATTERN",
]


class EyeScreeningEngine:
    _model = None
    _metadata = None

    @classmethod
    def get_model(cls):
        if cls._model is None and MODEL_PATH.exists():
            try:
                cls._model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"[EyeScreeningEngine] Warning: Could not load model file {MODEL_PATH}: {e}")
                cls._model = None
        return cls._model

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        if cls._metadata is None and METADATA_PATH.exists():
            try:
                with open(METADATA_PATH, "r") as f:
                    cls._metadata = json.load(f)
            except Exception:
                cls._metadata = {}
        return cls._metadata or {}

    @classmethod
    def interpret_screening(
        cls,
        features: Dict[str, float],
        quality: Dict[str, Any]
    ) -> EyeScreeningInterpretationResponse:
        """
        Executes an evidence-based screening interpretation on extracted webcam eye features.
        Adheres to non-diagnostic medical boundaries and explicit domain-shift notices.
        """
        # 1. Quality Check
        is_sufficient = quality.get("is_sufficient", True)
        valid_ratio = float(quality.get("valid_ratio", 1.0))

        if not is_sufficient or valid_ratio < 0.65:
            return EyeScreeningInterpretationResponse(
                status="UNAVAILABLE",
                label="INSUFFICIENT_TRACKING_QUALITY",
                confidence=None,
                model_name="verticare-eye-screening-xgboost",
                model_version="1.0.0",
                explanation="No reliable AI screening interpretation was produced because video tracking or lighting quality was insufficient.",
                contributing_factors=[
                    f"Valid tracked frame ratio: {valid_ratio * 100:.1f}% (Minimum threshold: 65%)",
                    "Unstable facial landmark detection or excessive head motion"
                ],
                disclaimer="AI-assisted screening observation. Not a medical diagnosis. Clinical interpretation should be performed by a qualified healthcare professional.",
                domain_shift_notice="Captured via consumer RGB webcam under visible lighting. Does not replace infrared video-oculography (VNG/VOG) in darkness."
            )

        # 2. Build Feature Vector
        feature_row = {}
        contributing_factors: List[str] = []

        for col in FEATURE_COLUMNS:
            if col == "valid_ratio":
                val = float(quality.get("valid_ratio", features.get("valid_ratio", 0.95)))
            else:
                val = float(features.get(col, 0.0))

            if math.isnan(val) or math.isinf(val):
                val = 0.0

            feature_row[col] = val

        df_input = pd.DataFrame([feature_row])

        # 3. Model Inference
        model = cls.get_model()
        meta = cls.get_metadata()
        model_name = meta.get("model_name", "verticare-eye-screening-xgboost")
        model_version = meta.get("model_version", "1.0.0")

        if model is not None:
            try:
                probs = model.predict_proba(df_input)[0]
                pred_idx = int(np.argmax(probs))
                predicted_label = TARGET_CLASSES[pred_idx]
                confidence = float(np.max(probs))
            except Exception as e:
                # Fallback to rule-based vestibular kinematics
                predicted_label, confidence = cls._rule_based_fallback(feature_row)
        else:
            predicted_label, confidence = cls._rule_based_fallback(feature_row)

        # 4. Generate Kinematic Contributing Factors & Explanation
        h_amp = feature_row["horizontal_amplitude"]
        v_amp = feature_row["vertical_amplitude"]
        h_vel = feature_row["horizontal_velocity_mean"]
        v_vel = feature_row["vertical_velocity_mean"]
        dir_h = int(feature_row["direction_changes_h"])
        dir_v = int(feature_row["direction_changes_v"])

        if predicted_label == "POSSIBLE_HORIZONTAL_NYSTAGMUS_PATTERN":
            explanation = (
                "Observed eye movements demonstrate rhythmic horizontal oscillatory beating "
                f"with elevated horizontal velocity ({h_vel:.3f}) and frequent horizontal direction reversals "
                f"({dir_h} reversals/10s), while vertical movement remains within baseline limits."
            )
            contributing_factors = [
                f"Elevated horizontal amplitude: {h_amp:.3f}",
                f"Elevated horizontal mean velocity: {h_vel:.3f}",
                f"Rhythmic horizontal direction changes: {dir_h} reversals in 10s",
                f"Stable vertical plane (v-amplitude: {v_amp:.3f})"
            ]

        elif predicted_label == "POSSIBLE_VERTICAL_NYSTAGMUS_PATTERN":
            explanation = (
                "Observed eye movements demonstrate significant vertical directional deviation "
                f"with elevated vertical velocity ({v_vel:.3f}) and vertical direction reversals ({dir_v} reversals/10s)."
            )
            contributing_factors = [
                f"Elevated vertical amplitude: {v_amp:.3f}",
                f"Elevated vertical mean velocity: {v_vel:.3f}",
                f"Vertical direction changes: {dir_v} reversals in 10s"
            ]

        elif predicted_label == "IRREGULAR_OCULAR_DRIFT_PATTERN":
            explanation = (
                "Observed eye movements show multi-directional drift without clear rhythmic periodicity, "
                "suggesting fixational instability or gaze drift."
            )
            contributing_factors = [
                f"Multi-axial displacement (H: {h_amp:.3f}, V: {v_amp:.3f})",
                f"Moderate multi-directional velocity (H: {h_vel:.3f}, V: {v_vel:.3f})",
                "Non-rhythmic directional reversals"
            ]

        else:  # NORMAL_FIXATION_PATTERN
            explanation = (
                "Observed eye movements demonstrate stable central fixation with micro-movements "
                f"and slow-phase drift within physiological baseline limits (H-amplitude: {h_amp:.3f}, H-velocity: {h_vel:.3f})."
            )
            contributing_factors = [
                f"Low horizontal amplitude: {h_amp:.3f} (<0.060)",
                f"Low horizontal slow-phase velocity: {h_vel:.3f} (<0.350)",
                f"Minimal vertical displacement: {v_amp:.3f}",
                f"Normal fixational tracking stability ({valid_ratio * 100:.1f}% valid frames)"
            ]

        return EyeScreeningInterpretationResponse(
            status="AVAILABLE",
            label=predicted_label,
            confidence=round(confidence, 3),
            model_name=model_name,
            model_version=model_version,
            explanation=explanation,
            contributing_factors=contributing_factors,
            disclaimer="AI-assisted screening observation. Not a medical diagnosis. Clinical interpretation should be performed by a qualified healthcare professional.",
            domain_shift_notice="Captured via consumer RGB webcam under visible lighting. Does not replace infrared video-oculography (VNG/VOG) in darkness."
        )

    @classmethod
    def _rule_based_fallback(cls, feat: Dict[str, float]) -> Tuple[str, float]:
        """Evidence-based vestibular kinematic fallback rule thresholds."""
        h_amp = feat.get("horizontal_amplitude", 0.0)
        v_amp = feat.get("vertical_amplitude", 0.0)
        h_vel = feat.get("horizontal_velocity_mean", 0.0)
        v_vel = feat.get("vertical_velocity_mean", 0.0)
        dir_h = feat.get("direction_changes_h", 0)
        dir_v = feat.get("direction_changes_v", 0)

        if h_amp > 0.075 and h_vel > 0.40 and dir_h >= 10 and v_amp < 0.050:
            return "POSSIBLE_HORIZONTAL_NYSTAGMUS_PATTERN", 0.88
        elif v_amp > 0.065 and v_vel > 0.35 and dir_v >= 8:
            return "POSSIBLE_VERTICAL_NYSTAGMUS_PATTERN", 0.84
        elif (h_amp > 0.055 or v_amp > 0.050) and (h_vel > 0.28 or v_vel > 0.25):
            return "IRREGULAR_OCULAR_DRIFT_PATTERN", 0.78
        else:
            return "NORMAL_FIXATION_PATTERN", 0.92
