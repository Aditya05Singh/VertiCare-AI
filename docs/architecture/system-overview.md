# VertiCare AI — Global Architecture Overview

## 1. System Topology

VertiCare AI is organized as a decoupled three-tier architecture with strict boundaries between presentation, business logic/inference, and persistence layers.

```mermaid
graph TB
    subgraph ClientLayer["Frontend Presentation Tier (React 18 / Vite / Tailwind)"]
        PatientSPA["Patient Portal\n• Dashboard\n• Daily Log\n• Adaptive Questionnaire\n• CV Eye Screening\n• Risk Overview\n• Emergency Triage"]
        DoctorSPA["Clinician Portal\n• Cohort KPI Dashboard\n• Patient List & Filter\n• Detailed Monitoring Dossier\n• Clinical Notes Editor\n• Emergency Queue"]
    end

    subgraph APILayer["Application & Inference Tier (FastAPI / Python 3.13)"]
        AuthModule["Auth & Security Engine\n(bcrypt / JWT HS256)"]
        HealthModule["Health Monitoring Engine\n(Symptom Aggregation / Trends)"]
        QEngine["Adaptive Questionnaire Tree\n(Deterministic Branching)"]
        CVEngine["Eye Kinematic Engine\n(MediaPipe / OpenCV / Kinematics)"]
        MLEngine["Multimodal Risk Engine\n(XGBoost / Imputation / Factors)"]
        DoctorModule["Clinician Management & Dossier"]
        EmergencyModule["Safety Escalation & Audit Trail"]
    end

    subgraph DataLayer["Persistence Tier (PostgreSQL 16 / SQLite Engine)"]
        RelationalDB[(Relational Database)]
    end

    PatientSPA -->|REST API over HTTPS| APILayer
    DoctorSPA -->|REST API over HTTPS| APILayer

    APILayer --> RelationalDB
```

## 2. Core Architectural Guarantees
1. **Zero Database Access from Frontend:** The client communicates exclusively through RESTful JSON APIs.
2. **Server-Side Authorization & Anti-IDOR:** Relational access checks (`require_patient`, `require_doctor`, `require_doctor_patient_access`) enforce data isolation on every API route.
3. **Graceful Multimodal Inference:** The ML Risk Engine can execute predictions with complete data (health check + questionnaire + eye features) or partial data using validated clinical medians/fallback imputation.
4. **Non-Diagnostic Safety Design:** All patient-facing and clinician-facing screens include non-diagnostic disclaimers and explicit emergency escalation guidance.

