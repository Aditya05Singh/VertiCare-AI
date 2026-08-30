# VertiCare AI — Backend Application

## 1. Overview
The VertiCare AI backend is a high-performance Python 3.13 / FastAPI application providing RESTful APIs for authentication, health monitoring, deterministic branching clinical questionnaires, computer vision kinematic feature persistence, offline machine learning risk inference, and clinician patient monitoring dossier aggregation.

## 2. Directory Layout
```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py          # FastAPI dependencies (require_patient, require_doctor, require_doctor_patient_access)
│   │   └── routes/          # REST endpoints (auth, health_checks, questionnaire, eye_analysis, risk, doctor, emergency, assignments)
│   ├── core/                # Configuration settings, logging, and security utilities (bcrypt, JWT)
│   ├── db/                  # SQLAlchemy engine, session management, and startup schema synchronization
│   ├── models/              # SQLAlchemy 2.0 ORM database entities
│   ├── schemas/             # Pydantic v2 data validation schemas
│   ├── services/            # Business logic, orchestration, and inference service layer
│   └── main.py              # Application factory and ASGI entrypoint
├── alembic/                 # Alembic migration scripts and database version tracking
├── tests/                   # Pytest test suite covering endpoints, models, security, and authorization
├── alembic.ini              # Alembic environment configuration
└── requirements.txt         # Production Python dependencies
```

## 3. Technology Stack
- **Framework:** FastAPI 0.115, Uvicorn, Starlette
- **Database:** PostgreSQL 16 / SQLite fallback, SQLAlchemy 2.0, Alembic
- **Security:** PyJWT, Passlib (bcrypt), Pydantic v2
- **Testing:** Pytest 9.1, HTTPX, Pytest-Asyncio

## 4. Local Execution
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## 5. Running Tests
```bash
MPLCONFIGDIR=/tmp PYTHONPATH=.:backend:cv:ml pytest tests/ -v
```
