# Daily Health Monitoring API Specification

This document details the RESTful API endpoints for recording and retrieving daily patient health check-ins and longitudinal symptom/lifestyle trends under `/api/health-checks` (and `/api/v1/health-checks`).

---

## Authorization Invariant
All endpoints require authentication with role **`PATIENT`**. The requesting patient's identity is derived strictly from the verified JWT access token. Attempts by clinicians or other patients to create, read, or manipulate another patient's health records return HTTP 403 or 404 (IDOR-safe).

---

## Endpoints

### 1. `POST /api/health-checks`
Record or update a daily health check for the authenticated patient.

- **Authentication:** Bearer JWT (Role: `PATIENT`)
- **Idempotence:** Single record per patient per calendar day (`UniqueConstraint("patient_id", "check_date")`). Subsequent submissions on the same day update the existing record.

**Request Payload:**
```json
{
  "check_date": "2026-08-31",
  "dizziness_severity": 6,
  "episode_duration": "1-20 minutes",
  "imbalance_severity": 5,
  "nausea": true,
  "headache": false,
  "sleep_hours": 6.5,
  "hydration_level": "Moderate (1-2L)",
  "stress_level": 7,
  "medication_adherence": "Taken as prescribed",
  "triggers": [
    "Sudden head movement",
    "Stress / Fatigue"
  ],
  "notes": "Felt unsteady when rising quickly in the morning."
}
```

**Response (HTTP 201 Created):**
```json
{
  "id": "e4b6c8a2-3f1d-4e5c-9a8b-7d6e5f4a3b2c",
  "patient_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
  "check_date": "2026-08-31",
  "dizziness_severity": 6,
  "episode_duration": "1-20 minutes",
  "imbalance_severity": 5,
  "nausea": true,
  "headache": false,
  "sleep_hours": 6.5,
  "hydration_level": "Moderate (1-2L)",
  "stress_level": 7,
  "medication_adherence": "Taken as prescribed",
  "triggers": [
    "Sudden head movement",
    "Stress / Fatigue"
  ],
  "notes": "Felt unsteady when rising quickly in the morning.",
  "created_at": "2026-08-31T01:25:00Z",
  "updated_at": "2026-08-31T01:25:00Z"
}
```

---

### 2. `GET /api/health-checks`
Retrieve chronological history of daily health checks for the authenticated patient.

- **Authentication:** Bearer JWT (Role: `PATIENT`)
- **Query Parameters:**
  - `limit` (int, default: 30, max: 100)
  - `offset` (int, default: 0)

**Response (HTTP 200 OK):**
```json
{
  "items": [
    {
      "id": "e4b6c8a2-3f1d-4e5c-9a8b-7d6e5f4a3b2c",
      "patient_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
      "check_date": "2026-08-31",
      "dizziness_severity": 6,
      "episode_duration": "1-20 minutes",
      "imbalance_severity": 5,
      "nausea": true,
      "headache": false,
      "sleep_hours": 6.5,
      "hydration_level": "Moderate (1-2L)",
      "stress_level": 7,
      "medication_adherence": "Taken as prescribed",
      "triggers": ["Sudden head movement"],
      "notes": "Morning unsteadiness.",
      "created_at": "2026-08-31T01:25:00Z",
      "updated_at": "2026-08-31T01:25:00Z"
    }
  ],
  "total": 1,
  "limit": 30,
  "offset": 0
}
```

---

### 3. `GET /api/health-checks/trends`
Compute aggregated longitudinal trends and time-series data points for frontend charts.

- **Authentication:** Bearer JWT (Role: `PATIENT`)
- **Query Parameters:**
  - `days` (int, default: 30, max: 90, e.g. `7` or `30`)

**Response (HTTP 200 OK):**
```json
{
  "patient_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
  "days_range": 7,
  "total_records": 4,
  "average_dizziness": 4.5,
  "average_imbalance": 3.2,
  "average_sleep": 7.1,
  "average_stress": 4.0,
  "data_points": [
    {
      "date": "2026-08-28",
      "dizziness_severity": 5,
      "imbalance_severity": 4,
      "sleep_hours": 7.0,
      "stress_level": 5,
      "hydration_level": "Moderate (1-2L)",
      "nausea": false,
      "headache": false,
      "episode_duration": "1-20 minutes"
    }
  ]
}
```

---

### 4. `GET /api/health-checks/{id}`
Retrieve a single health check record by unique identifier.

- **Authentication:** Bearer JWT (Role: `PATIENT`)
- **Security:** If the record ID belongs to another patient, returns `HTTP 404 Not Found` without disclosing record metadata.

