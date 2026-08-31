# VertiCare AI — Clinical Decision Support & Vertigo Monitoring System

> **ACADEMIC HEALTHCARE PROTOTYPE NOTICE:**  
> VertiCare AI is an academic healthcare software prototype engineered for vertigo screening, continuous daily monitoring, and clinician decision support. **It is NOT a clinically validated medical device** and does not diagnose conditions, prescribe medications, or replace the clinical evaluation of an ENT specialist, neurologist, or other qualified healthcare provider.

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph Client["React 18 + Vite SPA Frontend"]
        UI_Patient["Patient Portal\n(Dashboard, Health Log, Adaptive Questionnaire, Eye Screening, Risk, Emergency)"]
        UI_Doctor["Doctor Portal\n(Dashboard, Assigned Patients, Clinical Dossier, Notes, Reports)"]
        API_Client["Axios Client with JWT Interceptors"]
    end

    subgraph Backend["FastAPI High-Performance Backend"]
        Router_Auth["Auth Routes (/auth)"]
        Router_Patient["Patient Monitoring (/health-checks)"]
        Router_Questionnaire["Adaptive Questionnaire (/questionnaire)"]
        Router_Eye["Eye Analysis & Kinematics (/eye-analysis)"]
        Router_Risk["Multimodal Risk Engine (/risk-assessments)"]
        Router_Doctor["Clinician Dossier & Notes (/doctor)"]
        Router_Emergency["Emergency Events (/emergency)"]
        Router_Assignment["Doctor-Patient Assignment (/assignments)"]
        
        AuthService["Auth & Security Engine (bcrypt, JWT)"]
        RiskEngine["Multimodal Risk Predictor (XGBoost)"]
        EyeScreeningEngine["Eye Kinematic Screening Engine"]
        QuestionnaireEngine["Deterministic Adaptive Decision Tree"]
    end

    subgraph Database["PostgreSQL 16 / SQLite Engine"]
        DB_Users["Users & Profiles"]
        DB_Assignments["Doctor-Patient Assignments"]
        DB_Health["Daily Health Checks & Trends"]
        DB_Questionnaire["Questionnaire Sessions & Answers"]
        DB_Eye["Eye Sessions & Movement Features"]
        DB_Risk["Risk Assessments & Factors"]
        DB_Notes["Clinician Notes"]
        DB_Emergency["Emergency Events & Audits"]
    end

    UI_Patient --> API_Client
    UI_Doctor --> API_Client
    API_Client --> Backend
    Backend --> Database
    Backend --> RiskEngine
    Backend --> EyeScreeningEngine
    Backend --> QuestionnaireEngine
```

---

## 2. Implemented Modules (15 Core Modules)

1. **Authentication & Identity:** Role-based authentication (PATIENT / DOCTOR) with bcrypt password hashing and secure HS256 JWT tokens.
2. **Patient Account & Profiles:** Patient demographic data, medical histories, emergency contacts, and active doctor linkage.
3. **Doctor Account & Profiles:** Specialization, medical license registration, assigned cohort management.
4. **Patient / Doctor Authorization:** Server-side anti-IDOR checks enforcing strict patient tenant isolation and verified doctor-patient assignments.
5. **Daily Health Monitoring:** Severity tracking (dizziness, imbalance, nausea, tinnitus, headache), trigger logs, and longitudinal trend analytics.
6. **Adaptive Questionnaire:** Deterministic branching clinical tree (10 clinical questions) mapping vertigo onset, triggers, and duration.
7. **Computer Vision Eye-Movement Screening:** Real-time MediaPipe facial mesh landmark tracking, extracting 10 kinematic features (amplitudes, velocities, directional reversals, blink rates).
8. **ML Risk Engine:** Offline-trained XGBoost / Gradient Boosting multimodal risk prediction engine with graceful fallback imputation.
9. **Risk Assessment:** Calibrated risk tiers (LOW, MEDIUM, HIGH) with contributing factor breakdown and non-diagnostic disclaimers.
10. **Patient Longitudinal History:** Consolidated timeline across symptom checks, screening questionnaires, eye tests, and clinical notes.
11. **Doctor Dashboard:** Live clinician KPI overview, risk distribution breakdown, and real-time patient activity feed.
12. **Doctor Patient Monitoring Dossier:** Comprehensive sub-navigation view of assigned patient health history, eye kinematics, and questionnaires.
13. **Doctor Clinical Notes:** Clinician observation logging with privacy sharing controls and audit timestamps.
14. **Clinical Summary Reports:** Comprehensive multi-modal summary reports for patient records with clinical disclaimers.
15. **Emergency Support & Red-Flag Escalation:** Red-flag triage for acute symptoms, emergency contact integration, and clinician alert resolution workflows.

---

## 3. Technology Stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, Uvicorn, HTTPX.
- **Machine Learning & CV:** XGBoost, Scikit-Learn, Joblib, MediaPipe, OpenCV.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, TanStack Query v5, React Router v6, Lucide React, Recharts.
- **Database & Deployment:** PostgreSQL 16 Alpine / SQLite fallback, Docker & Docker Compose, Nginx.

---

## 4. Local Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+ (Node 20+ recommended)
- Docker & Docker Compose (optional for PostgreSQL)

### Running Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Running Frontend
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Full test suite across backend, CV, and ML
MPLCONFIGDIR=/tmp PYTHONPATH=.:backend:cv:ml backend/.venv/bin/pytest backend/tests/ cv/tests/ ml/tests/ -v

# Frontend TypeScript check and production build
cd frontend
npm run build
```

---

## 5. Deployment Architectures

### A. Cloud Deployment (Vercel + Render)
- **Frontend (Vercel):** Serves the React 18 / Vite SPA with automated SPA routing and `/api/*` reverse-proxying.
- **Backend & Database (Render):** Deploys FastAPI web service and managed PostgreSQL database via `render.yaml`.
- **Single Public URL:** Users access `https://<vercel-domain>`, and API requests to `/api/v1` are securely proxied behind the scenes to Render.

See full instructions in [Deployment Guide](docs/deployment/deployment.md).

### B. Local Container Deployment (Docker Compose)
```bash
docker compose up -d --build
```
This builds and starts PostgreSQL (port 5432), FastAPI Backend (port 8000), and Nginx Frontend (port 80).
