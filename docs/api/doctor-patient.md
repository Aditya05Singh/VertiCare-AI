# Doctor-Patient API Reference

## 1. Assignment Management Endpoints

### `POST /api/assignments`
Creates a mutual clinical assignment between a doctor and patient.
- **Authorization:** `DOCTOR` or `PATIENT` (JWT Bearer Token)
- **Request Body:**
  ```json
  {
    "patient_id": "34916d35-5368-47dc-8953-ceb739e93acc",  // Used when doctor initiates
    "doctor_id": "5efc4bfa-4f0d-4c8b-b123-d055b9fdba6e"    // Used when patient initiates
  }
  ```
- **Response Status:** `201 Created`
- **Response Body:**
  ```json
  {
    "id": "assignment-uuid",
    "doctor_id": "doctor-profile-uuid",
    "patient_id": "patient-profile-uuid",
    "doctor_user_id": "doctor-user-uuid",
    "patient_user_id": "patient-user-uuid",
    "doctor_name": "Dr. Marcus Einthoven",
    "doctor_specialization": "Vestibular Neurology",
    "doctor_license": "LIC-12345",
    "patient_name": "Krishna Gupta",
    "patient_email": "krishna@example.com",
    "assigned_at": "2026-08-31T02:00:00Z",
    "notice": "Active mutual clinical assignment between clinician and patient."
  }
  ```
- **Errors:**
  - `400 Bad Request`: Target account role mismatch (e.g. attempting to assign doctor to doctor).
  - `404 Not Found`: Target ID does not exist.
  - `409 Conflict`: Assignment relationship already exists.

---

### `GET /api/patient/assigned-doctor`
Retrieves the currently assigned clinician for the authenticated patient.
- **Authorization:** `PATIENT` (JWT Bearer Token)
- **Response Status:** `200 OK`
- **Response Body:**
  ```json
  {
    "has_assigned_doctor": true,
    "assignment_id": "assignment-uuid",
    "doctor_id": "doctor-profile-uuid",
    "doctor_user_id": "doctor-user-uuid",
    "doctor_name": "Dr. Marcus Einthoven",
    "specialization": "Vestibular Neurology",
    "license_identifier": "LIC-12345",
    "assigned_at": "2026-08-31T02:00:00Z"
  }
  ```

---

### `DELETE /api/assignments/{assignment_id}`
Terminates an active clinical assignment.
- **Authorization:** Assigned `DOCTOR` or Assigned `PATIENT`
- **Response Status:** `200 OK`
- **Response Body:**
  ```json
  {
    "message": "Assignment relationship successfully removed."
  }
  ```

---

## 2. Clinician Patient Monitoring Endpoints

### `GET /api/doctor/patients` / `GET /api/doctor/assigned-patients`
Lists authorized patients assigned to the authenticated clinician with search, risk filters, and sorting.
- **Authorization:** `DOCTOR` (JWT Bearer Token)
- **Query Parameters:**
  - `search`: string (filters by full name or email)
  - `risk_filter`: `HIGH` | `MEDIUM` | `LOW` | `UNASSESSED`
  - `sort_by`: `recent` | `risk_high_to_low` | `name`
- **Response Status:** `200 OK`
- **Response Body:**
  ```json
  {
    "items": [
      {
        "patient_id": "patient-profile-uuid",
        "full_name": "Krishna Gupta",
        "email": "krishna@example.com",
        "date_of_birth": "1990-07-20",
        "gender": "MALE",
        "assigned_at": "2026-08-31T02:00:00Z",
        "latest_risk_level": "LOW",
        "latest_risk_score": 0.18,
        "latest_assessment_date": "2026-08-31T02:15:00Z",
        "latest_health_check_date": "2026-08-31",
        "latest_health_check_dizziness": 4,
        "total_health_checks": 12
      }
    ],
    "total": 1
  }
  ```

---

### `GET /api/doctor/patients/{patient_id}`
Retrieves the comprehensive clinical dossier for an assigned patient.
- **Authorization:** `require_doctor_patient_access` (JWT Bearer Token with active assignment)
- **Path Parameter:** `patient_id` (matches `PatientProfile.id` or `User.id`)
- **Response Status:** `200 OK`
- **Response Body:** Contains patient demographic profile, latest health check, latest questionnaire, latest eye analysis with AI screening interpretation, latest risk assessment, and clinical note count.
- **Errors:**
  - `401 Unauthorized`: Missing or invalid JWT token.
  - `403 Forbidden`: Authenticated user is not a clinician.
  - `404 Not Found`: Patient not found or not assigned to the requesting clinician (Anti-IDOR).

---

### Patient Modality Sub-Endpoints (Clinician Access)
All sub-endpoints enforce `require_doctor_patient_access`:
- `GET /api/doctor/patients/{patient_id}/health`: Chronological health checks.
- `GET /api/doctor/patients/{patient_id}/health/trends?days=14`: Longitudinal rolling symptom averages.
- `GET /api/doctor/patients/{patient_id}/questionnaire`: Completed screening questionnaires.
- `GET /api/doctor/patients/{patient_id}/eye-analysis`: Eye tracking sessions with kinematic features and AI screening interpretations.
- `GET /api/doctor/patients/{patient_id}/risk`: AI multimodal risk assessment history.
- `GET /api/doctor/patients/{patient_id}/notes`: Clinical decision support notes.
- `POST /api/doctor/patients/{patient_id}/notes`: Author a new clinical note.
- `GET /api/doctor/patients/{patient_id}/reports`: Consolidated clinical report summary.

