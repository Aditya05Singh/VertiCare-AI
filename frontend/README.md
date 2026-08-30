# VertiCare AI — Frontend Application

## 1. Overview
The VertiCare AI frontend is a single-page application built with React 18, TypeScript, and Vite. It provides dedicated clinician and patient portals with real-time MediaPipe facial mesh eye-tracking, interactive adaptive questionnaires, daily symptom monitoring trend charts, and acute emergency escalation interfaces.

## 2. Directory Layout
```text
frontend/src/
├── api/            # Axios HTTP client, request/response interceptors, and typed API endpoints
├── components/     # Reusable UI component library (Button, Card, Modal, Input, HUD reticle)
├── constants/      # Clinical constants, question codes, and navigation routes
├── hooks/          # Custom React hooks (useAuth, useWebcam, useHealthTrends)
├── layouts/        # Application shells (PatientLayout, DoctorLayout, DoctorPatientLayout, AuthLayout)
├── lib/            # Utility configurations (Tailwind clsx/cva merge helpers)
├── pages/
│   ├── auth/       # Login, Patient Registration, Doctor Registration
│   ├── patient/    # Patient Dashboard, Daily Check, Questionnaire, Eye Analysis, Risk, Reports
│   ├── doctor/     # Doctor Dashboard, Assigned Patients, Dossier, Notes, Reports, Emergency
│   └── error/      # 404 Not Found, Access Denied, Server Error boundaries
├── types/          # TypeScript interfaces matching backend Pydantic schemas
├── App.tsx         # Main router setup and TanStack Query provider
└── main.tsx        # React DOM entry point
```

## 3. Technology Stack
- **Framework:** React 18.3, TypeScript 5.5, Vite 5.4
- **Styling:** Tailwind CSS 3.4, Lucide React icons
- **State & Query Cache:** TanStack Query (React Query) v5
- **Routing:** React Router v6
- **Computer Vision:** `@mediapipe/face_mesh`, `@mediapipe/camera_utils`
- **Charts:** Recharts 2.12

## 4. Local Execution
```bash
npm install
npm run dev
```

## 5. Production Build Verification
```bash
npm run build
```
Compiled assets will be output to the `dist/` directory.
