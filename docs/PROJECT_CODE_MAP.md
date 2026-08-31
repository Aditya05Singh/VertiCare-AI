# VertiCare AI — Project Code Map

This document provides a comprehensive mapping of the VertiCare AI codebase, connecting each clinical domain and module to its exact frontend components, backend routes, services, schemas, and persistence models.

---

## 1. Top-Level Directory Topology

```text
VertiCare-AI/
├── frontend/               # React 18 / Vite / TypeScript client SPA
├── backend/                # FastAPI / SQLAlchemy 2.0 / Pydantic application server
├── ml/                     # Machine learning models, training scripts, and preprocessing
├── cv/                     # Computer vision MediaPipe eye-tracking & kinematics
├── docs/                   # System architecture, API specs, database schemas, security & privacy
├── docker/                 # Production Dockerfiles and Nginx reverse proxy configuration
├── scripts/                # Development scripts and utilities
├── uploads/                # Local runtime upload placeholder (zero raw video storage)
├── .github/                # GitHub Actions CI/CD workflows
├── docker-compose.yml      # Local container orchestration definition
└── README.md               # Primary project documentation and quickstart
```

---

## 2. Domain & Module File Map

### A. Authentication & Identity
- **Frontend Views:** `frontend/src/pages/auth/Login.tsx`, `RegisterPatient.tsx`, `RegisterDoctor.tsx`
- **Frontend API:** `frontend/src/api/authApi.ts`
- **Backend Route:** `backend/app/api/routes/auth.py`
- **Service Layer:** `backend/app/services/auth_service.py`
- **Security Engine:** `backend/app/core/security.py`
- **Schemas:** `backend/app/schemas/auth.py`
- **Models:** `backend/app/models/user.py`, `backend/app/models/profile.py`

### B. Daily Health Monitoring
- **Frontend Views:** `frontend/src/pages/patient/DailyHealthCheck.tsx`, `HealthTrendsChart.tsx`
- **Frontend API:** `frontend/src/api/healthApi.ts`
- **Backend Route:** `backend/app/api/routes/health_checks.py`
- **Service Layer:** `backend/app/services/health_check_service.py`
- **Schemas:** `backend/app/schemas/monitoring.py`
- **Models:** `backend/app/models/monitoring.py`

### C. Adaptive Screening Questionnaire
- **Frontend Views:** `frontend/src/pages/patient/AdaptiveQuestionnaire.tsx`
- **Frontend API:** `frontend/src/api/questionnaireApi.ts`
- **Backend Route:** `backend/app/api/routes/questionnaire.py`
- **Service Layer:** `backend/app/services/questionnaire_service.py`
- **Core Decision Engine:** `backend/app/services/questionnaire_engine.py`
- **Schemas:** `backend/app/schemas/questionnaire.py`
- **Models:** `backend/app/models/questionnaire.py`

### D. Computer Vision & Eye Movement Screening
- **Frontend Views:** `frontend/src/pages/patient/EyeAnalysis.tsx`, `frontend/src/components/camera/WebcamHUD.tsx`
- **Frontend API:** `frontend/src/api/eyeAnalysisApi.ts`
- **CV Algorithms:** `cv/src/cv_pipeline.py`, `eye_features.py`, `movement_analysis.py`, `validation.py`
- **Backend Route:** `backend/app/api/routes/eye_analysis.py`
- **Service Layer:** `backend/app/services/eye_analysis_service.py`
- **Inference Engine:** `backend/app/services/eye_screening_engine.py`
- **Schemas:** `backend/app/schemas/eye_analysis.py`
- **Models:** `backend/app/models/eye_analysis.py`

### E. Multimodal ML Risk Engine
- **Frontend Views:** `frontend/src/pages/patient/RiskAssessmentView.tsx`, `RiskResultCard.tsx`
- **Frontend API:** `frontend/src/api/riskApi.ts`
- **ML Training & Inference:** `ml/src/train.py`, `ml/src/predict.py`, `ml/src/feature_engineering.py`
- **Model Artifacts:** `ml/models/verticare-risk-v1.joblib`, `eye-screening-v1.joblib`
- **Backend Route:** `backend/app/api/routes/risk_assessments.py`
- **Service Layer:** `backend/app/services/risk_service.py`
- **Schemas:** `backend/app/schemas/risk.py`
- **Models:** `backend/app/models/risk.py`

### F. Doctor Portal & Patient Dossier
- **Frontend Views:** `frontend/src/pages/doctor/DoctorDashboard.tsx`, `DoctorPatientList.tsx`, `DoctorPatientOverview.tsx`, `DoctorPatientHealthHistory.tsx`, `DoctorPatientEyeAnalysis.tsx`, `DoctorPatientQuestionnaire.tsx`, `DoctorPatientRiskHistory.tsx`, `DoctorPatientNotes.tsx`, `DoctorPatientReport.tsx`
- **Layout Shell:** `frontend/src/layouts/DoctorPatientLayout.tsx`
- **Frontend API:** `frontend/src/api/doctorApi.ts`
- **Backend Route:** `backend/app/api/routes/doctor.py`
- **Service Layer:** `backend/app/services/doctor_service.py`
- **Schemas:** `backend/app/schemas/doctor.py`
- **Models:** `backend/app/models/notes.py`

### G. Emergency Escalation System
- **Frontend Views:** `frontend/src/pages/patient/EmergencySupport.tsx`, `frontend/src/pages/doctor/DoctorEmergencyEvents.tsx`
- **Frontend API:** `frontend/src/api/emergencyApi.ts`
- **Backend Route:** `backend/app/api/routes/emergency.py`
- **Service Layer:** `backend/app/services/emergency_service.py`
- **Schemas:** `backend/app/schemas/emergency.py`
- **Models:** `backend/app/models/emergency.py`

### H. Doctor-Patient Mutual Assignment
- **Frontend Views:** `frontend/src/pages/patient/PatientAssignedDoctor.tsx`, `frontend/src/pages/doctor/DoctorPatientList.tsx`
- **Backend Route:** `backend/app/api/routes/assignment.py`
- **Service Layer:** `backend/app/services/assignment_service.py`
- **Schemas:** `backend/app/schemas/assignment.py`
- **Models:** `backend/app/models/profile.py` (`DoctorPatient` table)

### I. Deployment & Infrastructure
- **Vercel Frontend Reverse Proxy & SPA Config:** `vercel.json`, `frontend/vercel.json`
- **Render Backend & Managed DB Blueprint:** `render.yaml`
- **Python Version Lock:** `.python-version` (3.11.9)
- **Container Infrastructure:** `docker-compose.yml`, `docker/Dockerfile.backend`, `docker/Dockerfile.frontend`, `docker/nginx.conf`
- **Continuous Integration Pipeline:** `.github/workflows/ci.yml`

