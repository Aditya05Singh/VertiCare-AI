# Evidence-Based Eye Screening Model & Kinematic Interpretation

## 1. Executive Summary & Clinical Context
VertiCare AI's Computer Vision module records ocular kinematic movements during a structured 10-second fixation and pursuit task. Rather than outputting uninterpreted raw coordinates, the system employs an evidence-based screening classifier (`verticare-eye-screening-xgboost`, version `1.0.0`) to classify observed eye-movement dynamics into physiological and pathophysiological pattern archetypes.

---

## 2. Research Grounding & Scientific Literature
This model's kinematic feature space, velocity thresholds, and target definitions are grounded in published vestibular video-oculography (VNG/VOG) and neurotology literature:

1. **Lim et al. (2019)**: *Developing a Diagnostic Decision Support System for Benign Paroxysmal Positional Vertigo Using a Deep-Learning Model* (Journal of Clinical Medicine 2019, 8(5), 633; DOI: [10.3390/jcm8050633](https://doi.org/10.3390/jcm8050633)).
   - **Context:** Evaluated 91,778 nystagmus video clips from 3,467 dizzy patients across Seoul National University Bundang Hospital annotated by 4 otology specialists.
   - **Accessibility:** Institutional clinical hospital repository (IRB B-1808/486-104); cited as peer-reviewed parameter reference for vestibular nystagmus temporal modeling.
2. **Newman-Toker et al. (2013)** & **Mantokoudis et al. (2015)**: Quantitative slow-phase velocity (SPV) thresholds in acute vestibular syndrome:
   - Physiological fixational stability: SPV $< 2.0^\circ$/s.
   - Pathological spontaneous/positional nystagmus: SPV $> 4.0^\circ$/s.
3. **Zhang et al. (2021)** & **Weng et al. (2023)**: Automated classification of nystagmus using video-oculography feature representations.

---

## 3. Dataset Accessibility & Integrity Statement
- **Proprietary Clinical Datasets:** Clinical hospital VNG datasets (e.g., SNUBH clinical repository) require institutional data transfer agreements (DTA) and IRB approval; VertiCare AI explicitly does **not** claim unauthorized possession of proprietary patient hospital video archives.
- **Parametric Research Dataset:** For offline training and benchmarking, VertiCare constructed a research-grounded oculomotor kinematic dataset ($N=160$ patients, 640 sessions) parameterized from published VNG/VOG kinematic distributions.
- **Leakage Prevention:** Split strictly at the **patient level** using `GroupShuffleSplit` (70% train, 15% validation, 15% test) to ensure no patient sessions overlap between training and evaluation cohorts.

---

## 4. Feature Schema
The model operates on 11 numerical kinematic features extracted from the 10-second session:
- `horizontal_amplitude`: Maximum/mean horizontal displacement amplitude.
- `vertical_amplitude`: Maximum/mean vertical displacement amplitude.
- `horizontal_velocity_mean`: Mean velocity along the horizontal axis.
- `vertical_velocity_mean`: Mean velocity along the vertical axis.
- `horizontal_velocity_max`: Peak horizontal velocity (saccadic / fast-phase component).
- `vertical_velocity_max`: Peak vertical velocity.
- `direction_changes_h`: Frequency of directional reversals on horizontal plane (nystagmus beat count).
- `direction_changes_v`: Frequency of directional reversals on vertical plane.
- `blink_count`: Total detected blinks.
- `blink_rate_per_min`: Blinks per minute.
- `valid_ratio`: Proportion of valid tracked frames over session duration.

---

## 5. Target Classification Schema
The model categorizes observed kinematics into 4 distinct patterns:
1. **`NORMAL_FIXATION_PATTERN`**: Low amplitude ($<0.060$), low slow-phase velocity ($<0.350$), minimal vertical deviation, high tracking stability.
2. **`POSSIBLE_HORIZONTAL_NYSTAGMUS_PATTERN`**: Elevated horizontal velocity ($>0.400$), rhythmic horizontal direction reversals ($\ge 10$ reversals/10s), stable vertical plane.
3. **`POSSIBLE_VERTICAL_NYSTAGMUS_PATTERN`**: Elevated vertical amplitude and velocity ($>0.350$) with rhythmic vertical direction reversals.
4. **`IRREGULAR_OCULAR_DRIFT_PATTERN`**: Multi-axial displacement and moderate velocities without clear rhythmic periodicity.

---

## 6. Multi-Model Evaluation Results

| Model | Val F1 (Macro) | Test Accuracy | Test Precision (Macro) | Test Recall (Macro) | Test F1 (Macro) | Test ROC-AUC (OVR) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Standardized)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| **Random Forest (120 Trees)** | 0.9880 | 0.9896 | 0.9902 | 0.9890 | 0.9895 | 0.9995 |
| **Gradient Boosting Classifier** | 0.9850 | 0.9896 | 0.9890 | 0.9890 | 0.9890 | 0.9990 |

---

## 7. Critical Domain Shift & Clinical Limitations Notice

> [!WARNING]
> **Consumer RGB Webcam Domain Shift:**
> Clinical Video-Nystagmography (VNG) goggles operate using high-frequency infrared cameras (100–250 fps) in complete darkness with fixation suppression. VertiCare AI operates on standard consumer RGB webcams (30 fps) under room lighting. Ambient lighting, glare, reflections, and conscious fixation can suppress peripheral vestibular nystagmus.

> [!IMPORTANT]
> **Non-Diagnostic Medical Disclaimer:**
> VertiCare AI eye-movement screening results are AI-assisted screening observations intended to support clinician review. They do not constitute a medical diagnosis and do not replace formal laboratory VNG or clinical neurotological examination.

