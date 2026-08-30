# Clinician Dashboard Architecture & Monitoring Control

This document outlines the architecture, data security model, and clinical decision support integration for the VertiCare AI Doctor Dashboard.

---

## 1. Authorization & Access Control Flow

All clinician-patient interactions follow strict assignment-based authorization:

```
Doctor
  │
  ▼
Authentication (JWT Bearer Token)
  │
  ▼
Doctor Role Verification (UserRole.DOCTOR)
  │
  ▼
DoctorProfile Record Validation
  │
  ▼
Assigned Patient Check (DoctorPatient table lookup)
  │
  ▼
Patient Multimodal Data Access
  ├── Health History & Trends (Daily Health Checks)
  ├── Questionnaire History (Adaptive Branching Sessions)
  ├── Eye Analysis Kinematics (Webcam CV Metrics)
  ├── AI Risk Trajectory (Model Scores & Contributing Factors)
  ├── Clinician Decision Support Notes (Manual Authoring & Editing)
  └── Consolidated Clinical Reports (Structured Summaries)
```

---

## 2. Security & Anti-IDOR Enforcement

- **IDOR Protection:** Clinicians cannot view, query, or append notes to any patient not assigned to them in the `doctor_patients` relation.
- **Uniform Error Handling:** In accordance with security best practices, accessing an unassigned patient returns `HTTP 404 Not Found` rather than `403 Forbidden` to prevent leaking whether an unauthorized patient ID exists.
- **Note Immutability Across Clinicians:** Only the authoring doctor may edit their clinical notes. Modification attempts by other clinicians return `HTTP 403 Forbidden`.

---

## 3. Medical Safety & Non-Diagnostic Decision Support

> [!CAUTION]
> **Prototype Safety Boundary**
>
> 1. The Doctor Dashboard presents patient-reported tracking, computer-vision observations, and AI risk estimations to assist clinician triage and review.
> 2. The platform does **not** assert automatic disease diagnoses (e.g., BPPV, Meniere's disease) or generate automatic clinical prescriptions.
> 3. Clinical notes are entered manually by licensed clinicians without automated generative AI synthesis.

