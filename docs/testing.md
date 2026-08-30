# VertiCare AI Testing Strategy & Test Execution

## 1. Overview
VertiCare AI employs a multi-tiered testing suite covering backend APIs, authentication, authorization/anti-IDOR security, database models, computer vision feature extraction, machine learning risk engine, and frontend TypeScript static type validation.

## 2. Test Suites

### A. Backend Integration & API Tests (`backend/tests/`)
- `test_auth.py`: Patient/Doctor registration, duplicate email rejection, login, token issuance.
- `test_role_authorization.py`: Role enforcement, patient isolation, doctor route protection.
- `test_database_models.py`: Relational integrity, cascades, uniqueness constraints.
- `test_health_checks.py`: Daily symptom logging, same-day upsert logic, trend calculations.
- `test_questionnaire.py`: Deterministic tree traversal, branching validation, resume, anti-IDOR.
- `test_eye_analysis_api.py`: Feature persistence, quality threshold validation, role boundaries.
- `test_risk_assessment_api.py`: Multimodal fusion, missing modality defaults, security.
- `test_doctor_api.py`: Clinician dashboard KPIs, dossier aggregation, clinical notes lifecycle.
- `test_emergency_api.py`: Emergency event creation, doctor review and resolution lifecycle.
- `test_patient_record_access_and_eye_screening.py`: Mutual assignment validation, full dossier sub-endpoints, eye screening interpretation.

### B. Computer Vision Tests (`cv/tests/`)
- `test_cv_eye_features.py`: Euclidean distance, eye aspect ratio (EAR), normalized position.
- `test_cv_movement_analysis.py`: Velocity, amplitude, direction changes, quality summary.
- `test_cv_pipeline.py`: Synthetic frame pipeline, low-quality frame drop detection.
- `test_cv_validation.py`: Finite number validation, unrecognized key detection, NaN handling.

### C. Machine Learning Tests (`ml/tests/`)
- `test_ml_data_loader.py`: Benchmark data generation, patient-level stratification.
- `test_ml_data_validation.py`: Schema validation, impossible value detection.
- `test_ml_feature_engineering.py`: Modality aggregation, fallback imputation, factor extraction.
- `test_ml_predict.py`: Multimodal RiskPredictor inference, calibrated risk scores.
- `test_ml_preprocessing.py`: StandardScaler, OneHotEncoder, and ColumnTransformer integrity.

## 3. Running Test Suites

```bash
# Set Python path and run pytest across backend, cv, and ml
MPLCONFIGDIR=/tmp PYTHONPATH=.:backend:cv:ml backend/.venv/bin/pytest backend/tests/ cv/tests/ ml/tests/ -v

# Frontend TypeScript and Production Build Verification
cd frontend
npm run build
```

## 4. Test Results Summary
- **Backend/CV/ML Pytest Suite:** 93 passed, 0 failed (100% pass rate).
- **Frontend Type & Build Verification:** 0 TypeScript compiler errors, production bundle compiled cleanly.

