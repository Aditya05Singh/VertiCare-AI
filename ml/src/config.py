import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "synthetic_demo_dataset.csv"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODEL_NAME = "XGBoost"
MODEL_VERSION = "verticare-risk-v1"
MODEL_PATH = MODELS_DIR / f"{MODEL_VERSION}.joblib"
METADATA_PATH = MODELS_DIR / f"{MODEL_VERSION}_metadata.json"
REPORT_PATH = REPORTS_DIR / "model_evaluation_summary.json"

# Controlled 3-level screening risk classes
RISK_CLASSES = ["LOW", "MEDIUM", "HIGH"]
TARGET_COLUMN = "risk_level"

# Random Seed for Reproducibility
RANDOM_STATE = 42

# Explicitly Defined Feature Columns
NUMERICAL_FEATURES = [
    # Daily Monitoring (Step 4)
    "dizziness_severity",
    "imbalance_severity",
    "stress_level",
    "sleep_hours",
    "trigger_count",
    # Computer Vision (Step 6)
    "cv_horizontal_amplitude",
    "cv_vertical_amplitude",
    "cv_horizontal_velocity_mean",
    "cv_vertical_velocity_mean",
    "cv_direction_changes_h",
    "cv_blink_rate_per_min",
    "cv_valid_ratio",
]

CATEGORICAL_FEATURES = [
    # Daily Monitoring
    "episode_duration",
    "hydration_level",
    "medication_adherence",
    # Questionnaire (Step 5)
    "q_functional_impact",
    "q_non_spin_type",
    "q_head_turns",
]

BOOLEAN_FEATURES = [
    # Daily Monitoring
    "has_nausea",
    "has_headache",
    # Questionnaire (Step 5)
    "q_spinning",
    "q_positional",
    "q_orthostatic",
    "q_gait_difficulty",
    "q_auditory_symptoms",
    "q_recent_infection",
]

ALL_FEATURE_COLUMNS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + BOOLEAN_FEATURES

