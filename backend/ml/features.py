from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

FEATURE_COLUMNS: List[str] = [
    "symptom_dizziness_severity",      # 1-10
    "symptom_nausea_severity",         # 1-10
    "symptom_unsteadiness_severity",   # 1-10
    "symptom_sleep_hours",             # 0-24
    "symptom_stress_level",            # 1-10
    "q_vertigo_type_spinning",         # 0 or 1
    "q_vertigo_type_lightheaded",      # 0 or 1
    "q_duration_seconds_to_hours",     # 1: seconds, 2: minutes/hours, 3: days
    "q_trigger_head_movement",         # 0 or 1
    "q_trigger_spontaneous",           # 0 or 1
    "q_hearing_loss_present",          # 0 or 1
    "q_tinnitus_present",              # 0 or 1
    "q_neurologic_deficit_flag",       # 0 or 1 (Critical Red Flag)
    "q_functional_impact_score",       # 0: none, 1: mild, 2: mod, 3: severe
    "eye_horizontal_drift_vel",        # float
    "eye_vertical_drift_vel",          # float
    "eye_oscillation_freq_hz",         # float (1.0 - 6.0 Hz)
    "eye_oscillation_amplitude",       # float
    "eye_fixation_stability_score",    # 0 - 100
    "eye_saccade_count",               # int
    "eye_nystagmoid_flag",             # 0 or 1
    "patient_age"                      # int (years)
]


def extract_feature_vector(
    health_check: Optional[Any] = None,
    questionnaire_answers: Optional[Dict[str, Any]] = None,
    eye_features: Optional[Any] = None,
    patient_age: int = 45
) -> np.ndarray:
    """
    Extract a normalized 22-dimensional feature vector from multi-modal domain objects.
    """
    q_map = questionnaire_answers or {}

    # 1. Symptom features
    diz = float(health_check.dizziness_severity) if health_check else 4.0
    nau = float(health_check.nausea_severity) if health_check else 2.0
    unst = float(health_check.unsteadiness_severity) if health_check else 3.0
    sleep = float(health_check.sleep_hours) if health_check else 7.5
    stress = float(health_check.stress_level) if health_check else 5.0

    # 2. Questionnaire features
    sensation = q_map.get("Q_SENSATION_TYPE", "")
    spin_flag = 1.0 if sensation == "true_spinning" else 0.0
    light_flag = 1.0 if sensation == "lightheadedness" else 0.0

    dur = q_map.get("Q_EPISODE_DURATION", "minutes_to_hours")
    dur_score = 1.0 if dur == "seconds" else (3.0 if dur == "days_constant" else 2.0)

    triggers = q_map.get("Q_TRIGGER_FACTORS", [])
    head_trig = 1.0 if any(t in triggers for t in ["turning_in_bed", "looking_up_bending", "head_movement_general"]) else 0.0
    spon_trig = 1.0 if "spontaneous_no_trigger" in triggers else 0.0

    otologic = q_map.get("Q_OTOLOGIC_SYMPTOMS", [])
    hearing_loss = 1.0 if "hearing_loss_unilateral" in otologic else 0.0
    tinnitus = 1.0 if "tinnitus_ringing" in otologic else 0.0

    neuro = q_map.get("Q_NEUROLOGIC_RED_FLAGS", [])
    neuro_flag = 1.0 if any(n in neuro for n in ["slurred_speech", "facial_weakness_numbness", "double_vision", "limb_weakness_clumsiness", "swallowing_difficulty"]) else 0.0

    impact = q_map.get("Q_DAILY_IMPACT_DHI", "mildly_limited")
    impact_map = {"not_limited": 0.0, "mildly_limited": 1.0, "moderately_limited": 2.0, "severely_limited": 3.0}
    impact_score = impact_map.get(impact, 1.0)

    # 3. Eye Movement Features
    if eye_features:
        h_drift = float(eye_features.horizontal_drift_velocity)
        v_drift = float(eye_features.vertical_drift_velocity)
        freq_hz = float(eye_features.oscillation_frequency_hz)
        amp = float(eye_features.oscillation_amplitude)
        stability = float(eye_features.gaze_fixation_stability_score)
        saccades = float(eye_features.saccade_count)
        nystagmus = 1.0 if eye_features.nystagmoid_pattern_detected else 0.0
    else:
        h_drift = 0.02
        v_drift = 0.01
        freq_hz = 0.0
        amp = 0.0
        stability = 88.0
        saccades = 2.0
        nystagmus = 0.0

    vector = np.array([
        diz, nau, unst, sleep, stress,
        spin_flag, light_flag, dur_score, head_trig, spon_trig,
        hearing_loss, tinnitus, neuro_flag, impact_score,
        h_drift, v_drift, freq_hz, amp, stability, saccades, nystagmus,
        float(patient_age)
    ], dtype=float)

    return vector
