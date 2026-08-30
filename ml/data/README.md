# VertiCare AI — ML Data Directory

This directory stores raw and processed data definitions for the multimodal risk classification engine.

---

## Directory Layout
- `raw/`: Raw data definitions and synthetic benchmark dataset (`synthetic_demo_dataset.csv`).
- `processed/`: Serialized feature arrays (when generated).

---

## Data Schema & Feature Matrix
All models consume the standardized 26-feature multimodal matrix defined in `ml/src/config.py`:
- 12 Numerical features
- 6 Categorical features
- 8 Boolean features

Personal identifiers (`patient_id`, `email`, `name`, `phone`, timestamps) are strictly prohibited from entering training or inference feature arrays.

