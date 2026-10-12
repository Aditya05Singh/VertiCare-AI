"""
ml/src/general_symptom_engine/config.py

Configuration and schema definitions for the Experimental General-Symptom Engine,
trained on the Kaggle Disease Symptoms and Patient Profile Dataset.
"""

from pathlib import Path
from typing import List, Dict

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "disease_symptoms_and_patient_profile_dataset.csv"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODEL_NAME = "GeneralSymptomClassifier"
MODEL_VERSION = "general-symptom-v1"
ASSESSMENT_TYPE = "EXPERIMENTAL_GENERAL_SYMPTOM_ASSESSMENT"

MODEL_PATH = MODELS_DIR / f"{MODEL_VERSION}.joblib"
METADATA_PATH = MODELS_DIR / f"{MODEL_VERSION}_metadata.json"
REPORT_PATH = REPORTS_DIR / "general_symptom_model_report.json"

RANDOM_STATE = 42

# Column specifications in Kaggle dataset
TARGET_COLUMN = "Outcome Variable"
DISEASE_NAME_COLUMN = "Disease"

BINARY_SYMPTOMS: List[str] = [
    "Fever",
    "Cough",
    "Fatigue",
    "Difficulty Breathing",
]

NUMERICAL_DEMOGRAPHICS: List[str] = [
    "Age",
]

CATEGORICAL_PROFILES: List[str] = [
    "Gender",
    "Blood Pressure",
    "Cholesterol Level",
]

ALL_FEATURE_COLUMNS = BINARY_SYMPTOMS + NUMERICAL_DEMOGRAPHICS + CATEGORICAL_PROFILES

TARGET_MAP: Dict[str, int] = {"Positive": 1, "Negative": 0}
INV_TARGET_MAP: Dict[int, str] = {1: "Positive", 0: "Negative"}

VALID_GENDERS = {"Male", "Female"}
VALID_BP_LEVELS = {"Low", "Normal", "High"}
VALID_CHOLESTEROL_LEVELS = {"Low", "Normal", "High"}
VALID_BINARY_ANSWERS = {"Yes", "No", True, False, 1, 0}

