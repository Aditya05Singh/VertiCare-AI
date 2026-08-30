# Machine Learning & AI Risk Engine Pipeline

This document outlines the machine learning architecture, feature engineering from multimodal sources, training and model selection strategies, and non-diagnostic risk calibration in VertiCare AI.

---

## 1. Objective & Scope

The ML Risk Engine provides an AI-assisted vestibular screening risk estimate categorized into **`LOW`**, **`MEDIUM`**, or **`HIGH`** tiers, paired with a calibrated risk score $[0.0, 1.0]$ and explainable contributing factors.

```
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│ Daily Health Check (S4) │  │ Questionnaire Resp (S5) │  │ CV Kinematics (S6)      │
└────────────┬────────────┘  └────────────┬────────────┘  └────────────┬────────────┘
             │                            │                            │
             └──────────────────────┐     │     ┌──────────────────────┘
                                    ▼     ▼     ▼
                             ┌─────────────────────────┐
                             │ Feature Engineering     │
                             │ (Multimodal Aggregation)│
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │ Scikit-Learn Pipeline   │
                             │ (Impute, Scale, OHE)    │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │ Calibrated Classifier   │
                             │ (Logistic / XGBoost)    │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │ RiskAssessment Result   │
                             │ (LOW / MEDIUM / HIGH)   │
                             └─────────────────────────┘
```

---

## 2. Multimodal Input Features

| Feature Name | Source Modality | Type | Range / Encoding |
| :--- | :--- | :--- | :--- |
| `dizziness_severity` | Daily Health Check | Numeric | 0 to 10 |
| `imbalance_severity` | Daily Health Check | Numeric | 0 to 10 |
| `stress_level` | Daily Health Check | Numeric | 0 to 10 |
| `sleep_hours` | Daily Health Check | Numeric | 0.0 to 24.0 |
| `trigger_count` | Daily Health Check | Numeric | $\ge 0$ |
| `episode_duration` | Daily Health Check | Categorical | none, seconds, minutes, hours, constant |
| `hydration_level` | Daily Health Check | Categorical | good, moderate, poor |
| `medication_adherence`| Daily Health Check | Categorical | full, missed_dose, skipped, not_prescribed |
| `has_nausea` | Daily Health Check | Boolean | 0 or 1 |
| `has_headache` | Daily Health Check | Boolean | 0 or 1 |
| `q_spinning` | Questionnaire | Boolean | 0 or 1 |
| `q_positional` | Questionnaire | Boolean | 0 or 1 |
| `q_orthostatic` | Questionnaire | Boolean | 0 or 1 |
| `q_gait_difficulty` | Questionnaire | Boolean | 0 or 1 |
| `q_auditory_symptoms` | Questionnaire | Boolean | 0 or 1 |
| `q_recent_infection`| Questionnaire | Boolean | 0 or 1 |
| `q_functional_impact`| Questionnaire | Categorical | none, mild, moderate, severe |
| `q_non_spin_type` | Questionnaire | Categorical | none, unsteadiness, lightheaded, floating, vague |
| `q_head_turns` | Questionnaire | Categorical | none, right, left, both, lying_down, looking_up |
| `cv_horizontal_amplitude` | Computer Vision | Numeric | Normalized displacement ($\ge 0.0$) |
| `cv_vertical_amplitude` | Computer Vision | Numeric | Normalized displacement ($\ge 0.0$) |
| `cv_horizontal_velocity_mean` | Computer Vision | Numeric | Normalized units / sec |
| `cv_vertical_velocity_mean` | Computer Vision | Numeric | Normalized units / sec |
| `cv_direction_changes_h` | Computer Vision | Numeric | Count of sign reversals |
| `cv_blink_rate_per_min` | Computer Vision | Numeric | Blinks per minute |
| `cv_valid_ratio` | Computer Vision | Numeric | 0.0 to 1.0 |

---

## 3. Preprocessing & Data Leakage Prevention

- **Leakage Prevention:** Personal identifiers (`patient_id`, `email`, `user_id`, timestamps, names) are strictly excluded from feature matrices.
- **Data Transforms:**
  - Missing values in numerical features are imputed with the training set median, followed by standard scaling.
  - Categorical variables are one-hot encoded with `handle_unknown='ignore'`.
  - Missing modalities gracefully fallback to neutral baseline defaults.

---

## 4. Model Selection & Versioning

- **Candidate Models Compared:** Logistic Regression, Random Forest, Gradient Boosting / XGBoost.
- **Selection Criterion:** 5-Fold Stratified Cross-Validation Macro F1 Score.
- **Model Version Identifier:** `verticare-risk-v1` (stored alongside model artifacts and referenced in all `RiskAssessment` records).

---

## 5. Medical Safety Boundary

> [!CAUTION]
> **Academic Prototype Notice**
>
> The ML Risk Engine generates screening risk categories (`LOW`, `MEDIUM`, `HIGH`) to assist clinical prioritization.
> - It does **NOT** diagnose BPPV, Meniere's disease, or vestibular neuritis.
> - It does **NOT** replace an in-person physical examination or clinical diagnostic tests.

