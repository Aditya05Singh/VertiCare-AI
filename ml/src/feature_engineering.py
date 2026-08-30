from typing import Dict, Any, List, Optional
import numpy as np
from ml.src.config import ALL_FEATURE_COLUMNS


def extract_features_from_modalities(
    health_check: Optional[Dict[str, Any]] = None,
    questionnaire_answers: Optional[List[Dict[str, Any]]] = None,
    cv_features: Optional[Dict[str, float]] = None,
    cv_quality: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Deterministically transforms raw multimodal records (Daily Health Check,
    Adaptive Questionnaire responses, and CV Kinematics) into a sanitized feature vector.
    """
    features: Dict[str, Any] = {}

    # 1. Daily Health Check Modality (Step 4)
    if health_check:
        features["dizziness_severity"] = float(health_check.get("dizziness_severity", 0))
        features["imbalance_severity"] = float(health_check.get("imbalance_severity", 0))
        features["stress_level"] = float(health_check.get("stress_level", 0))
        features["sleep_hours"] = float(health_check.get("sleep_hours", 7.0))
        triggers = health_check.get("triggers", [])
        features["trigger_count"] = float(len(triggers) if isinstance(triggers, list) else 0)
        features["episode_duration"] = str(health_check.get("episode_duration", "none")).lower()
        features["hydration_level"] = str(health_check.get("hydration_level", "moderate")).lower()
        features["medication_adherence"] = str(health_check.get("medication_adherence", "not_prescribed")).lower()
        features["has_nausea"] = bool(health_check.get("nausea", False))
        features["has_headache"] = bool(health_check.get("headache", False))
    else:
        features["dizziness_severity"] = 0.0
        features["imbalance_severity"] = 0.0
        features["stress_level"] = 0.0
        features["sleep_hours"] = 7.0
        features["trigger_count"] = 0.0
        features["episode_duration"] = "none"
        features["hydration_level"] = "moderate"
        features["medication_adherence"] = "not_prescribed"
        features["has_nausea"] = False
        features["has_headache"] = False

    # 2. Adaptive Questionnaire Modality (Step 5)
    # Convert list of answers into a lookup map by question_code
    q_map: Dict[str, Any] = {}
    if questionnaire_answers:
        for item in questionnaire_answers:
            code = item.get("question_code")
            if code:
                q_map[code] = item.get("answer")

    features["q_spinning"] = bool(q_map.get("Q_SPINNING", False))
    features["q_positional"] = bool(q_map.get("Q_POSITIONAL", False))
    features["q_orthostatic"] = bool(q_map.get("Q_ORTHOSTATIC", False))
    features["q_gait_difficulty"] = bool(q_map.get("Q_GAIT_DIFFICULTY", False))
    features["q_recent_infection"] = bool(q_map.get("Q_INFECTION_RECENT", False))

    auditory_ans = q_map.get("Q_AUDITORY", [])
    if isinstance(auditory_ans, list) and any(x != "none" for x in auditory_ans):
        features["q_auditory_symptoms"] = True
    else:
        features["q_auditory_symptoms"] = False

    features["q_functional_impact"] = str(q_map.get("Q_FUNCTIONAL_IMPACT", "none")).lower()
    features["q_non_spin_type"] = str(q_map.get("Q_NON_SPIN_TYPE", "none")).lower()
    features["q_head_turns"] = str(q_map.get("Q_HEAD_TURNS", "none")).lower()

    # 3. Computer Vision Modality (Step 6)
    if cv_features:
        features["cv_horizontal_amplitude"] = float(cv_features.get("horizontal_amplitude", 0.0))
        features["cv_vertical_amplitude"] = float(cv_features.get("vertical_amplitude", 0.0))
        features["cv_horizontal_velocity_mean"] = float(cv_features.get("horizontal_velocity_mean", 0.0))
        features["cv_vertical_velocity_mean"] = float(cv_features.get("vertical_velocity_mean", 0.0))
        features["cv_direction_changes_h"] = float(cv_features.get("direction_changes_h", 0))
        features["cv_blink_rate_per_min"] = float(cv_features.get("blink_rate_per_min", 15.0))
    else:
        features["cv_horizontal_amplitude"] = 0.0
        features["cv_vertical_amplitude"] = 0.0
        features["cv_horizontal_velocity_mean"] = 0.0
        features["cv_vertical_velocity_mean"] = 0.0
        features["cv_direction_changes_h"] = 0.0
        features["cv_blink_rate_per_min"] = 15.0

    if cv_quality:
        features["cv_valid_ratio"] = float(cv_quality.get("valid_ratio", 0.0))
    else:
        features["cv_valid_ratio"] = 0.0

    return features


def identify_contributing_factors(feature_dict: Dict[str, Any]) -> List[str]:
    """
    Derives explainable, non-diagnostic contributing factors based directly on observed patient inputs.
    """
    factors: List[str] = []

    # Symptom severity factors
    dizz = feature_dict.get("dizziness_severity", 0.0)
    if dizz >= 7.0:
        factors.append(f"Elevated self-reported dizziness severity ({int(dizz)}/10)")
    elif dizz >= 4.0:
        factors.append(f"Moderate self-reported dizziness severity ({int(dizz)}/10)")

    imb = feature_dict.get("imbalance_severity", 0.0)
    if imb >= 7.0:
        factors.append(f"High postural imbalance rating ({int(imb)}/10)")

    # Functional impact factors
    func_impact = feature_dict.get("q_functional_impact", "none")
    if func_impact in ("severe", "moderate"):
        factors.append(f"Reported {func_impact} daily functional limitation")

    # Positional & Movement triggers
    if feature_dict.get("q_positional"):
        factors.append("Symptom onset triggered or aggravated by head position changes")

    if feature_dict.get("q_gait_difficulty"):
        factors.append("Difficulty maintaining steady walking or balance reported")

    if feature_dict.get("has_nausea"):
        factors.append("Presence of associated autonomic symptoms (nausea)")

    # Ocular movement factors
    cv_h_amp = feature_dict.get("cv_horizontal_amplitude", 0.0)
    cv_h_vel = feature_dict.get("cv_horizontal_velocity_mean", 0.0)
    if cv_h_amp > 0.06 or cv_h_vel > 0.40:
        factors.append("Elevated horizontal ocular drift or tracking velocity observed on screening")

    # Limit to top 4 factors
    if not factors:
        factors.append("Standard baseline screening features observed")

    return factors[:4]

