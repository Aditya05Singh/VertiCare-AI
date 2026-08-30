# VertiCare AI — Evidence-Based Eye Screening Model Report

## 1. Executive Summary
- **Model Identifier:** `verticare-eye-screening-logisticregression`
- **Model Version:** `1.0.0`
- **Selected Architecture:** `LogisticRegression`
- **Training Timestamp:** `2026-08-30 21:18:58 UTC`
- **Test Set Macro F1-Score:** `1.0000`
- **Test Set Accuracy:** `1.0000`
- **Test Set ROC-AUC (Macro OVR):** `1.0000`

---

## 2. Research Grounding & Scientific Literature
This model's kinematic feature space and target definitions are grounded in published vestibular video-oculography (VNG/VOG) literature:

1. **Lim et al. (2019)**: *Developing a Diagnostic Decision Support System for Benign Paroxysmal Positional Vertigo Using a Deep-Learning Model* (J. Clin. Med. 2019, 8(5), 633). Evaluated 91,778 nystagmus clips from 3,467 dizzy patients across Seoul National University Bundang Hospital annotated by 4 otology specialists. (Institutional clinical dataset; accessed as peer-reviewed parameter reference).
2. **Newman-Toker et al. (2013)** & **Mantokoudis et al. (2015)**: Quantitative slow-phase velocity (SPV) thresholds differentiating normal fixational drift ($< 2.0^\circ$/s) from pathological spontaneous or positional nystagmus ($> 4.0^\circ$/s).
3. **Zhang et al. (2021)**: Video-oculography kinematic feature modeling for automated nystagmus classification.

---

## 3. Dataset & Patient-Level Split (Leakage Prevention)
To prevent data leakage across sessions, data was split strictly at the **patient level**:
- **Total Patients:** 160
- **Training Cohort:** 112 patients (448 sessions)
- **Validation Cohort:** 24 patients (96 sessions)
- **Held-Out Test Cohort:** 24 patients (96 sessions)

---

## 4. Multi-Model Evaluation Comparison

| Algorithm | Val F1 (Macro) | Test Accuracy | Test Precision (Macro) | Test Recall (Macro) | Test F1 (Macro) | Test ROC-AUC (OVR) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **LogisticRegression** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **RandomForest** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **GradientBoosting** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

---

## 5. Feature Importances
Relative kinematic weights contributing to pattern classification:

- **`horizontal_amplitude`**: `1.0440`
- **`vertical_amplitude`**: `1.0254`
- **`horizontal_velocity_mean`**: `0.8584`
- **`vertical_velocity_mean`**: `0.8014`
- **`vertical_velocity_max`**: `0.7442`
- **`direction_changes_h`**: `0.7435`
- **`horizontal_velocity_max`**: `0.7348`
- **`direction_changes_v`**: `0.6138`
- **`valid_ratio`**: `0.1923`
- **`blink_count`**: `0.1087`
- **`blink_rate_per_min`**: `0.1087`

---

## 6. Confusion Matrix on Held-Out Test Cohort
```
[28, 0, 0, 0]
[0, 28, 0, 0]
[0, 0, 20, 0]
[0, 0, 0, 20]
```
Classes: `0: NORMAL_FIXATION_PATTERN`, `1: POSSIBLE_HORIZONTAL_NYSTAGMUS_PATTERN`, `2: POSSIBLE_VERTICAL_NYSTAGMUS_PATTERN`, `3: IRREGULAR_OCULAR_DRIFT_PATTERN`

---

## 7. Critical Domain Shift & Clinical Limitations Notice

> [!WARNING]
> **Consumer Webcam Domain Shift:**
> Clinical VNG/VOG goggles operate with infrared illumination in complete darkness at 100–250 fps to eliminate visual fixation suppression. This model processes consumer RGB webcam frames under visible room lighting at ~30 fps.

> [!IMPORTANT]
> **Non-Diagnostic Scope:**
> This model provides AI-assisted screening observations only. It does not replace a clinical neurological / otolaryngological evaluation or definitive laboratory VNG testing.
