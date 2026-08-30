# Clinician Portal & Patient Monitoring API Specification

This document defines the REST API endpoints under `/api/doctor` for clinician dashboard metrics, assigned patient directories, multimodal remote monitoring, clinical decision notes, and consolidated report summaries.

---

## 1. Security & Assignment-Based Authorization

```
                 Incoming Doctor API Request
                             │
                             ▼
               [JWT Authentication Verified]
                             │
                             ▼
               [Role Check: UserRole == DOCTOR]
                             │
                             ▼
              [DoctorProfile Record Resolution]
                             │
                             ▼
              [Patient ID Requested in Route]
                             │
                             ▼
             [DoctorPatient Assignment Lookup]
                     ┌───────┴───────┐
             Exists  │               │ Missing / Unassigned
                     ▼               ▼
              ACCESS GRANTED    HTTP 404 Not Found
                              (Anti-IDOR Protected)
```

> [!IMPORTANT]
> **Anti-IDOR Protection:**
> If a clinician requests data for a patient who is not explicitly assigned to them in `doctor_patients`, the backend returns **`HTTP 404 Not Found`**. This guarantees that unauthorized clinicians cannot determine whether a patient identifier exists within the system.

---

## 2. API Endpoints

### 2.1 `GET /api/doctor/dashboard`
Returns real aggregate KPI metrics and recent activity across the clinician's assigned patient cohort.

**Response (HTTP 200 OK):**
```json
{
  "total_assigned_patients": 4,
  "risk_distribution": {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 1,
    "UNASSESSED": 0
  },
  "recent_activity": [
    {
      "patient_id": "patient-uuid-1",
      "patient_name": "Alice Smith",
      "activity_type": "HEALTH_CHECK",
      "timestamp": "2026-08-31T01:30:00Z",
      "description": "Logged daily symptoms (Dizziness: 6/10, Imbalance: 5/10)",
      "risk_level": "MEDIUM"
    }
  ]
}
```

---

### 2.2 `GET /api/doctor/patients`
Retrieves a list of patients assigned to the authenticated doctor with search, risk filters, and sorting.

**Query Parameters:**
- `search` (string, optional): Full-text search over patient full name and email.
- `risk_filter` (string, optional): `HIGH`, `MEDIUM`, `LOW`, `UNASSESSED`.
- `sort_by` (string, default: `recent`): `recent`, `risk_high_to_low`, `name`.

**Response (HTTP 200 OK):**
```json
{
  "items": [
    {
      "patient_id": "patient-uuid-1",
      "full_name": "Alice Smith",
      "email": "alice@example.com",
      "date_of_birth": "1988-04-12",
      "gender": "FEMALE",
      "assigned_at": "2026-08-30T12:00:00Z",
      "latest_risk_level": "MEDIUM",
      "latest_risk_score": 0.52,
      "latest_assessment_date": "2026-08-31T01:30:00Z",
      "latest_health_check_date": "2026-08-31",
      "latest_health_check_dizziness": 6,
      "total_health_checks": 14
    }
  ],
  "total": 1
}
```

---

### 2.3 `GET /api/doctor/patients/{patient_id}`
Retrieves a summary dossier for the assigned patient.

**Response (HTTP 200 OK):**
```json
{
  "patient_id": "patient-uuid-1",
  "full_name": "Alice Smith",
  "email": "alice@example.com",
  "date_of_birth": "1988-04-12",
  "gender": "FEMALE",
  "medical_history": "History of mild migraine",
  "emergency_contact_name": "Bob Smith",
  "emergency_contact_phone": "+1-555-0199",
  "latest_health_check": { ... },
  "latest_questionnaire": { ... },
  "latest_eye_analysis": { ... },
  "latest_risk_assessment": { ... },
  "recent_notes_count": 2
}
```

---

### 2.4 `GET /api/doctor/patients/{patient_id}/health`
Retrieves paginated daily health checks. Supports `limit` and `offset`.

### 2.5 `GET /api/doctor/patients/{patient_id}/health/trends`
Calculates longitudinal multi-day averages and trend points. Supports `days` (default: 14).

### 2.6 `GET /api/doctor/patients/{patient_id}/questionnaire`
Retrieves all completed questionnaire screening sessions with question-answer breakdowns.

### 2.7 `GET /api/doctor/patients/{patient_id}/eye-analysis`
Retrieves all completed webcam eye-movement screening sessions with tracking quality indicators and extracted kinematic features.

### 2.8 `GET /api/doctor/patients/{patient_id}/risk`
Retrieves AI screening risk assessment history with model names (`LogisticRegression`, `XGBoost`), model versions (`verticare-risk-v1`), and explainable contributing factors.

---

### 2.9 `GET /api/doctor/patients/{patient_id}/notes` & `POST /api/doctor/patients/{patient_id}/notes`
Retrieve and create clinical decision support notes.

**Create Note Payload:**
```json
{
  "content": "Patient reports noticeable improvement after vestibular rehabilitation exercises.",
  "note_type": "ROUTINE_REVIEW",
  "is_shared_with_patient": true
}
```

### 2.10 `PATCH /api/doctor/notes/{note_id}`
Edit an existing note. Only the authoring doctor may update their own note (`HTTP 403 Forbidden` if another doctor attempts modification).

---

### 2.11 `GET /api/doctor/patients/{patient_id}/reports`
Compiles an aggregated multimodal clinical summary combining 14-day health averages, latest questionnaire answers, latest eye kinematics, latest AI risk estimation, and clinical notes.

