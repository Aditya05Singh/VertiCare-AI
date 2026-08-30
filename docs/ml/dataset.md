# ML Dataset Documentation

This document describes the dataset schema, modalities, and synthetic benchmarking status for the VertiCare AI machine learning subsystem.

---

## 1. Dataset Status

- **Status:** Synthetic Benchmarking & Pipeline Verification Dataset (`synthetic_benchmark_demo_dataset.csv`).
- **Purpose:** Software end-to-end testing, feature transformer validation, and cross-validation execution without fabricating unverified clinical trials.
- **Records Count:** 600 synthetic records ($N=480$ train, $N=120$ test).

---

## 2. Feature Modalities

1. **Daily Health Monitoring:** Dizziness severity (0–10), imbalance severity (0–10), stress level (0–10), sleep duration (hours), trigger count, episode duration, hydration level, medication adherence, nausea flag, headache flag.
2. **Adaptive Screening Questionnaire:** Spinning sensation, positional aggravation, orthostatic changes, gait difficulty, auditory symptoms (tinnitus/fullness), recent infection history, functional daily impact rating, non-spinning type, head turning directions.
3. **Computer Vision Eye Kinematics:** Horizontal amplitude, vertical amplitude, horizontal velocity mean, vertical velocity mean, direction changes count, blink rate per minute, tracking validity ratio.

---

## 3. Class Distribution

- **LOW:** ~10% of cohort (mild or non-interfering symptoms)
- **MEDIUM:** ~58% of cohort (moderate dizziness, isolated positional or transient triggers)
- **HIGH:** ~32% of cohort (severe imbalance, severe functional impact, high ocular drift)

