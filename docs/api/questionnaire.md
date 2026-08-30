# Adaptive Intelligent Questionnaire API Specification

This document details the RESTful API endpoints for managing adaptive questionnaire screening sessions under `/api/questionnaire` (and `/api/v1/questionnaire`).

---

## Authorization & Security Policy
- **Requirement:** Authenticated user with role **`PATIENT`**.
- **Cross-Patient Isolation:** IDOR attempts (accessing another patient's session or submitting answers into another session) return `HTTP 404 Not Found`.
- **Order Security:** Submitting answers out of turn returns `HTTP 400 Bad Request`.

---

## Endpoints

### 1. `GET /api/questionnaire/start`
Start a new questionnaire or resume an ongoing `IN_PROGRESS` session.

**Response (HTTP 200 OK):**
```json
{
  "session_id": "b3e9a1c4-6d8f-4a2b-9e0c-5f7d3a1b8c6e",
  "status": "IN_PROGRESS",
  "started_at": "2026-08-31T01:30:00Z",
  "completed_at": null,
  "current_question": {
    "id": "q1-uuid",
    "question_code": "Q_SPINNING",
    "version": "v1.0",
    "category": "sensation",
    "question_type": "BOOLEAN",
    "question_text": "Does the dizziness feel like you or the room is actively spinning around?",
    "options": [],
    "display_order": 1
  },
  "progress": {
    "answered_count": 0,
    "estimated_total": 6,
    "current_step": 1
  },
  "message": null
}
```

---

### 2. `GET /api/questionnaire/active`
Check if the authenticated patient has an existing incomplete questionnaire session.

**Response (HTTP 200 OK):** Returns `SessionResponse` if active session exists, or `null` if none.

---

### 3. `POST /api/questionnaire/session/{session_id}/answer`
Submit an answer to the current server-selected question.

**Request Payload:**
```json
{
  "question_code": "Q_SPINNING",
  "answer": true
}
```

**Response (HTTP 200 OK):**
```json
{
  "session_id": "b3e9a1c4-6d8f-4a2b-9e0c-5f7d3a1b8c6e",
  "status": "IN_PROGRESS",
  "started_at": "2026-08-31T01:30:00Z",
  "completed_at": null,
  "current_question": {
    "id": "q2-uuid",
    "question_code": "Q_POSITIONAL",
    "version": "v1.0",
    "category": "positional",
    "question_type": "BOOLEAN",
    "question_text": "Is the spinning sensation triggered or noticeably worsened by changing head position?",
    "options": [],
    "display_order": 2
  },
  "progress": {
    "answered_count": 1,
    "estimated_total": 6,
    "current_step": 2
  },
  "message": null
}
```

---

### 4. `POST /api/questionnaire/session/{session_id}/complete`
Manually mark an active session as completed.

**Response (HTTP 200 OK):** Returns `SessionResponse` with `status: "COMPLETED"`.

---

### 5. `GET /api/questionnaire/session/{session_id}/summary`
Retrieve non-diagnostic structured assessment summary.

**Response (HTTP 200 OK):**
```json
{
  "session_id": "b3e9a1c4-6d8f-4a2b-9e0c-5f7d3a1b8c6e",
  "patient_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
  "status": "COMPLETED",
  "started_at": "2026-08-31T01:30:00Z",
  "completed_at": "2026-08-31T01:33:00Z",
  "total_questions_answered": 6,
  "answers": [
    {
      "question_code": "Q_SPINNING",
      "question_text": "Does the dizziness feel like you or the room is actively spinning around?",
      "category": "sensation",
      "question_type": "BOOLEAN",
      "answer": true,
      "answered_at": "2026-08-31T01:30:30Z"
    }
  ],
  "notice": "This questionnaire is an academic screening prototype and does not represent a medical diagnosis or clinical prescription."
}
```

