# VertiCare AI — Production Deployment Guide

## 1. Architecture Overview

VertiCare AI is engineered for a seamless single-URL cloud deployment architecture:

```text
Browser (User)
      │
      ▼
Vercel (React 18 + Vite SPA)
      │
      │  /api/* (Reverse Proxy)
      ▼
Render (FastAPI Python Service)
      │
      ├── PostgreSQL Database (Managed PostgreSQL on Render)
      └── ML/CV Inference Engines (XGBoost + MediaPipe Kinematics)
```

- **Single Public Entry Point:** Users navigate strictly to the Vercel frontend URL (e.g. `https://verticare-ai.vercel.app`).
- **Seamless Proxying:** The browser issues relative API requests to `/api/...`, which Vercel securely proxies to the Render backend via `vercel.json` rewrites. The user never needs to visit or manually wake the backend.

---

## 2. Cloud Deployment (Vercel + Render)

### Step A: Deploy Backend & Database on Render
1. Navigate to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub repository (`https://github.com/Aditya05Singh/VertiCare-AI`).
4. Render will read `render.yaml` and provision:
   - **PostgreSQL Database:** `verticare-ai-db`
   - **Web Service:** `verticare-ai-backend`
5. Note your assigned Render backend service URL (e.g., `https://verticare-ai-backend.onrender.com`).
6. Verify backend health:
   ```bash
   curl https://<YOUR_RENDER_URL>/health
   # Expected: {"status":"ok","service":"verticare-backend"}
   ```

### Step B: Deploy Frontend on Vercel
1. Navigate to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** → **Project**.
3. Import the GitHub repository `https://github.com/Aditya05Singh/VertiCare-AI`.
4. Configure the Project:
   - **Framework Preset:** Vite
   - **Root Directory:** `./` (or `frontend`)
   - **Build Command:** `cd frontend && npm install && npm run build` (or `npm run build` if Root is `frontend`)
   - **Output Directory:** `frontend/dist` (or `dist` if Root is `frontend`)
5. If your Render backend URL differs from `https://verticare-ai-backend.onrender.com`, update the `destination` in `vercel.json` with your actual Render URL:
   ```json
   {
     "source": "/api/:match*",
     "destination": "https://<YOUR_RENDER_BACKEND_URL>/api/:match*"
   }
   ```
6. Click **Deploy**.

---

## 3. Environment Variables Specification

### Backend (Render Environment)
| Variable | Example Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://...` | Connection string to PostgreSQL instance |
| `SECRET_KEY` | *(Auto-generated 64-char string)* | JWT signing key |
| `ALGORITHM` | `HS256` | JWT cryptographic algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token validity duration (24h) |
| `APP_ENV` | `production` | Runtime mode |
| `DEBUG` | `false` | Disable debug tracebacks |
| `CORS_ORIGINS` | `https://*.vercel.app,http://localhost:5173` | Whitelisted cross-origin domains |

### Frontend (Vercel Environment)
No secrets are required in frontend environment variables. All requests route through relative `/api/v1` endpoints.

---

## 4. Local Deployment with Docker Compose

```bash
# Build and start PostgreSQL, Backend, and Frontend containers
docker compose up -d --build

# Verify container health
docker compose ps

# Backend Health: http://localhost:8000/health
# Frontend Portal: http://localhost:80
```
