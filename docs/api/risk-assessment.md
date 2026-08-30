# AI Risk Assessment API Specification

This document details the REST API endpoints for calculating and retrieving multimodal screening risk assessments under `/api/risk-assessment` (and `/api/v1/risk-assessment`).

---

## Authorization & Security Policy
- **Requirement:** Authenticated user with role **`PATIENT`**.
- **Cross-Patient Isolation:** IDOR attempts (accessing another patient's risk assessment) return `HTTP 404 Not Found`.
- **Doctor Prohibition:** Doctors are forbidden from calling the patient risk calculation endpoint (`HTTP 403 Forbidden`).

---

## Endpoints

### 1. `POST /api/risk-assessment`
Trigger multimodal data aggregation, ML model inference, and persistence of a new `RiskAssessment`.

**Request Payload (Optional):**
```json
{
  "health_check_id": "optional-uuid",
  "questionnaire_session_id": "optional-uuid",
  "eye_analysis_session_id": "optional-uuid"
}
```
*If omitted or empty, the server automatically queries the patient's latest recorded data across all 3 modalities.*

**Response (HTTP 200 OK):**
```json
{
  "id": "b7a2d4e8-1c9f-4a3b-8e2d-5f7c3a1b9e0f",
  "patient_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
  "health_check_id": "hc-uuid",
  "questionnaire_session_id": "q-uuid",
  "eye_analysis_session_id": "eye-uuid",
  "risk_score": 0.52,
  "risk_level": "MEDIUM",
  "model_name": "LogisticRegression",
  "model_version": "verticare-risk-v1",
  "contributing_factors": [
    "Moderate self-reported dizziness severity (6/10)",
    "Symptom onset triggered or aggravated by head position changes",
    "Presence of associated autonomic symptoms (nausea)"
  ],
  "created_at": "2026-08-31T01:45:00Z",
  "notice": "AI-assisted screening estimate for clinical decision support. Not a medical diagnosis."
}
```

---

### 2. `GET /api/risk-assessment/history`
Retrieve chronological history of assessments for the authenticated patient.

**Parameters:**
- `limit` (int, default: 10, min: 1, max: 100)
- `offset` (int, default: 0)

**Response (HTTP 200 OK):**
```json
{
  "items": [
    {
      "id": "b7a2d4e8-1c9f-4a3b-8e2d-5f7c3a1b9e0f",
      "patient_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
      "risk_score": 0.52,
      "risk_level": "MEDIUM",
      "model_name": "LogisticRegression",
      "model_version": "verticare-risk-v1",
      "contributing_factors": ["Moderate self-reported dizziness severity (6/10)"],
      "created_at": "2026-08-31T01:45:00Z",
      "notice": "AI-assisted screening estimate for clinical decision support. Not a medical diagnosis."
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

---

### 3. `GET /api/risk-assessment/{id}`
Retrieve a single risk assessment by ID.

**Response (HTTP 200 OK):** Returns `RiskAssessmentResponse`.

