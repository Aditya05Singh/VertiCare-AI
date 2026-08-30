# VertiCare AI — Machine Learning Pipeline

## 1. Overview
The `ml/` module contains data generation, validation, preprocessing, model training, evaluation, and serialized inference artifacts for the VertiCare AI Multimodal Vestibular Risk Engine and Eye Movement Screening Engine.

## 2. Directory Layout
```text
ml/
├── data/
│   ├── raw/                 # Raw benchmark and clinical cohort datasets
│   └── processed/           # Transformed, preprocessed tabular feature matrices
├── models/                  # Serialized Joblib model artifacts and metadata JSONs
│   ├── verticare-risk-v1.joblib
│   ├── verticare-risk-v1_metadata.json
│   ├── eye-screening-v1.joblib
│   └── eye-screening-v1_metadata.json
├── reports/                 # Markdown training reports and cross-validation metrics
├── src/
│   ├── data_loader.py       # Benchmark dataset generator and clinical stratification
│   ├── data_validation.py   # Schema integrity, range, and impossibility checks
│   ├── feature_engineering.py# Multimodal feature alignment, factor extraction, and imputation
│   ├── predict.py           # Real-time inference engine and fallback imputers
│   ├── preprocessing.py     # Scikit-learn ColumnTransformer pipelines
│   ├── train.py             # Multimodal risk model training script
│   └── train_eye_screening.py# Eye screening pattern classification training script
└── tests/                   # ML unit tests and prediction verification
```

## 3. Supported Model Architecture
- **Multimodal Vestibular Risk Predictor:** XGBoost / Gradient Boosting Classifier trained on fused daily symptom logs, structured questionnaire answers, and kinematic eye movement features.
- **Eye Screening Classifier:** Gradient Boosting Classifier classifying ocular drift and nystagmus kinematic patterns based on clinical vestibular literature benchmarks (Lim et al. 2019, Newman-Toker et al. 2013).

## 4. Retraining Models
```bash
python ml/src/train.py
python ml/src/train_eye_screening.py
```

## 5. Running ML Tests
```bash
MPLCONFIGDIR=/tmp PYTHONPATH=.:backend:ml pytest ml/tests/ -v
```
