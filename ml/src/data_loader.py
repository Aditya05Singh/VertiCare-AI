import os
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd
import numpy as np

from ml.src.config import (
    RAW_DATA_PATH,
    TARGET_COLUMN,
    RANDOM_STATE,
    ALL_FEATURE_COLUMNS,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    BOOLEAN_FEATURES,
)


def generate_synthetic_benchmark_data(num_samples: int = 600, random_state: int = RANDOM_STATE) -> pd.DataFrame:
    """
    Generates a deterministic synthetic benchmarking dataset for software pipeline verification.
    Clearly marked as synthetic/demonstration data (NOT real clinical data).
    """
    np.random.seed(random_state)

    patient_ids = [f"SYNTH-PAT-{i:04d}" for i in range(num_samples)]

    # 1. Numerical Features
    dizziness = np.random.randint(0, 11, size=num_samples)
    imbalance = np.random.randint(0, 11, size=num_samples)
    stress = np.random.randint(0, 11, size=num_samples)
    sleep = np.round(np.random.uniform(3.0, 10.0, size=num_samples), 1)
    triggers = np.random.randint(0, 6, size=num_samples)

    cv_h_amp = np.round(np.random.uniform(0.01, 0.12, size=num_samples), 4)
    cv_v_amp = np.round(np.random.uniform(0.005, 0.05, size=num_samples), 4)
    cv_h_vel = np.round(np.random.uniform(0.05, 0.90, size=num_samples), 4)
    cv_v_vel = np.round(np.random.uniform(0.02, 0.30, size=num_samples), 4)
    cv_dir_changes = np.random.randint(0, 15, size=num_samples)
    cv_blinks = np.round(np.random.uniform(5.0, 30.0, size=num_samples), 1)
    cv_valid_ratio = np.round(np.random.uniform(0.70, 1.00, size=num_samples), 3)

    # 2. Categorical Features
    ep_durations = np.random.choice(["none", "seconds", "minutes", "hours", "constant"], size=num_samples, p=[0.2, 0.3, 0.25, 0.15, 0.1])
    hydration = np.random.choice(["good", "moderate", "poor"], size=num_samples, p=[0.4, 0.4, 0.2])
    med_adherence = np.random.choice(["full", "missed_dose", "skipped", "not_prescribed"], size=num_samples, p=[0.5, 0.2, 0.1, 0.2])
    func_impact = np.random.choice(["none", "mild", "moderate", "severe"], size=num_samples, p=[0.25, 0.35, 0.25, 0.15])
    non_spin_type = np.random.choice(["none", "unsteadiness", "lightheaded", "floating", "vague"], size=num_samples)
    head_turns = np.random.choice(["none", "right", "left", "both", "lying_down", "looking_up"], size=num_samples)

    # 3. Boolean Features
    has_nausea = np.random.choice([True, False], size=num_samples, p=[0.35, 0.65])
    has_headache = np.random.choice([True, False], size=num_samples, p=[0.30, 0.70])
    q_spinning = np.random.choice([True, False], size=num_samples, p=[0.55, 0.45])
    q_positional = np.random.choice([True, False], size=num_samples, p=[0.40, 0.60])
    q_orthostatic = np.random.choice([True, False], size=num_samples, p=[0.25, 0.75])
    q_gait = np.random.choice([True, False], size=num_samples, p=[0.35, 0.65])
    q_auditory = np.random.choice([True, False], size=num_samples, p=[0.20, 0.80])
    q_infection = np.random.choice([True, False], size=num_samples, p=[0.15, 0.85])

    # Deterministic scoring for synthetic target label (LOW, MEDIUM, HIGH)
    severity_score = (
        dizziness * 1.5 +
        imbalance * 1.2 +
        (cv_h_amp * 40.0) +
        (cv_h_vel * 10.0) +
        (has_nausea.astype(int) * 3.0) +
        (q_positional.astype(int) * 4.0) +
        (func_impact == "severe").astype(int) * 6.0 +
        (func_impact == "moderate").astype(int) * 3.0
    )

    risk_levels = []
    for score in severity_score:
        if score < 16.0:
            risk_levels.append("LOW")
        elif score < 28.0:
            risk_levels.append("MEDIUM")
        else:
            risk_levels.append("HIGH")

    df = pd.DataFrame({
        "patient_id": patient_ids,
        "dizziness_severity": dizziness,
        "imbalance_severity": imbalance,
        "stress_level": stress,
        "sleep_hours": sleep,
        "trigger_count": triggers,
        "cv_horizontal_amplitude": cv_h_amp,
        "cv_vertical_amplitude": cv_v_amp,
        "cv_horizontal_velocity_mean": cv_h_vel,
        "cv_vertical_velocity_mean": cv_v_vel,
        "cv_direction_changes_h": cv_dir_changes,
        "cv_blink_rate_per_min": cv_blinks,
        "cv_valid_ratio": cv_valid_ratio,
        "episode_duration": ep_durations,
        "hydration_level": hydration,
        "medication_adherence": med_adherence,
        "q_functional_impact": func_impact,
        "q_non_spin_type": non_spin_type,
        "q_head_turns": head_turns,
        "has_nausea": has_nausea,
        "has_headache": has_headache,
        "q_spinning": q_spinning,
        "q_positional": q_positional,
        "q_orthostatic": q_orthostatic,
        "q_gait_difficulty": q_gait,
        "q_auditory_symptoms": q_auditory,
        "q_recent_infection": q_infection,
        "risk_level": risk_levels,
        "dataset_type": "SYNTHETIC_BENCHMARK_DEMO"
    })

    return df


def load_raw_dataset(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load raw dataset from CSV path, creating synthetic benchmark data if file doesn't exist."""
    path = csv_path or RAW_DATA_PATH
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        synthetic_df = generate_synthetic_benchmark_data(num_samples=600)
        synthetic_df.to_csv(path, index=False)
        return synthetic_df
    return pd.read_csv(path)

