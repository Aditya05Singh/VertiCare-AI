# Deployment Guide for VertiCare AI

## 1. Overview
VertiCare AI is packaged for deployment using Docker Compose, containerizing the FastAPI backend service, React/Vite SPA on Nginx, and PostgreSQL 16 database.

## 2. Architecture & Container Layout
- **PostgreSQL Database (`postgres`):** Relational store for users, profiles, health records, questionnaires, eye movements, risk predictions, clinical notes, and emergency events.
- **FastAPI Backend (`backend`):** High-performance ASGI Python 3.13 service executing business logic, JWT authentication, MediaPipe CV kinematics, and XGBoost ML inference.
- **Nginx Frontend (`frontend`):** Static build serving compiled React/Vite assets with reverse-proxy routing `/api` requests to the backend container.

## 3. Environment Variables
Copy `.env.example` to `.env` and configure appropriate production secrets:

```bash
cp .env.example .env
```

Key variables:
- `SECRET_KEY`: Minimum 32-character high-entropy random secret for JWT signing.
- `POSTGRES_DB`: Database name (e.g. `verticare_db`).
- `POSTGRES_USER`: Database username.
- `POSTGRES_PASSWORD`: Strong database password.
- `DATABASE_URL`: `postgresql://verticare_user:verticare_password@postgres:5432/verticare_db`
- `CORS_ORIGINS`: Allowed production host domains.

## 4. Local Deployment with Docker Compose

```bash
# Build and start all services in detached mode
docker compose up -d --build

# Inspect running container logs
docker compose logs -f

# Verify service health
curl -f http://localhost:8000/health

# Stop containers
docker compose down
```

## 5. Database Migrations in Production
Alembic migrations can be executed directly inside the backend container:

```bash
docker compose exec backend alembic upgrade head
```

## 6. Health & Liveness Checks
- Backend Liveness: `GET /health` -> `{"status": "ok", "app": "VertiCare AI"}`
- API v1 Health: `GET /api/v1/health` -> `{"status": "healthy", "service": "verticare-api"}`

