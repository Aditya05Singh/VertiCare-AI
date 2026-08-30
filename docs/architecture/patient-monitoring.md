# Patient Daily Health Monitoring Architecture

This document details the data lifecycle, architectural boundaries, and user interactions for the patient daily health monitoring subsystem in VertiCare AI.

---

## 1. System Data Flow

```
[ Authenticated Patient ]
         │
         ▼
[ React Form: /patient/health-check ]
         │  (Frontend Zod validation & range checks)
         ▼
[ API: POST /api/health-checks ]
         │  (JWT verify_token + require_patient dependency)
         ▼
[ HealthCheckService ]
         │  (Enforce 1 check per day idempotency)
         ▼
[ PostgreSQL: daily_health_checks ]
         │
         ├───> [ API: GET /api/health-checks/trends?days=7/30 ] ───> [ Recharts Symptom & Lifestyle Visualizations ]
         │
         └───> [ API: GET /api/health-checks ] ────────────────────> [ Patient History Table & Logs ]
```

---

## 2. Core Functional Responsibilities

1. **Daily Check-In Acquisition:**
   - Captures subjective symptom metrics (dizziness severity 0–10, imbalance severity 0–10, duration category, nausea, headache).
   - Captures lifestyle context (sleep duration in hours, hydration brackets, stress levels 0–10, medication adherence, environmental/physical triggers).
2. **Transactional & Idempotency Guarantee:**
   - Enforced by database constraint `UNIQUE(patient_id, check_date)`. Submitting again on the same calendar day updates the existing record rather than creating duplicate entries.
3. **Longitudinal Aggregation:**
   - Service calculates mathematical rolling averages for symptom severity and lifestyle metrics without executing heavy analytical pipelines.
   - Computes chronological time-series points consumed directly by SVG charts.

---

## 3. Medical Scope & Non-Diagnostic Boundary Notice

> [!IMPORTANT]
> **Academic Prototype & Non-Diagnostic Boundary**
>
> The Daily Health Monitoring subsystem strictly records self-reported monitoring information for tracking symptom trajectory over time.
>
> - It does **NOT** independently diagnose vestibular disorders (e.g. BPPV, Meniere's Disease, Vestibular Migraine, Labyrinthitis).
> - It does **NOT** provide pharmacological prescriptions or treatment directives.
> - All recorded symptom histories and trend charts are intended solely for academic research and as clinician reference during qualified medical consultations.

