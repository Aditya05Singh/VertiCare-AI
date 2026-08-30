# VertiCare AI — Computer Vision & Eye Kinematics

## 1. Overview
The `cv/` module contains the computer vision feature extraction pipeline, MediaPipe facial mesh integration, coordinate normalization, temporal kinematic calculations, and data validation rules for webcam-based eye movement screening.

## 2. Directory Layout
```text
cv/
├── src/
│   ├── cv_pipeline.py       # End-to-end frame stream processor and feature assembler
│   ├── eye_features.py      # MediaPipe FaceMesh iris/ocular landmark extraction
│   ├── movement_analysis.py # Kinematic velocity, amplitude, reversals, and blink metrics
│   └── validation.py        # Numerical sanity gates, finite checks, and payload validation
└── tests/                   # Unit tests for CV algorithms, synthetic frame tests, and error checks
```

## 3. Extracted Kinematic Features
- `horizontal_velocity_mean`: Mean horizontal ocular velocity
- `horizontal_velocity_max`: Peak horizontal ocular velocity
- `horizontal_amplitude`: Horizontal angular displacement
- `vertical_velocity_mean`: Mean vertical ocular velocity
- `vertical_velocity_max`: Peak vertical ocular velocity
- `vertical_amplitude`: Vertical angular displacement
- `direction_changes_h`: Frequency of horizontal directional reversals
- `direction_changes_v`: Frequency of vertical directional reversals
- `blink_count`: Total blink count during recording window
- `blink_rate_per_min`: Extrapolated blink frequency per minute

## 4. Quality Thresholds
- Minimum valid frame ratio: `0.70`
- Minimum face detection ratio: `0.70`
- Sessions with insufficient quality are marked as `INSUFFICIENT_QUALITY` and prevented from generating speculative risk predictions.

## 5. Running CV Tests
```bash
PYTHONPATH=.:cv pytest cv/tests/ -v
```
