# Authentication API Specification

This document details the RESTful authentication and user profile endpoints exposed under `/api/auth` (and `/api/v1/auth`).

---

## Endpoints Overview

### 1. `POST /api/auth/register/patient`
Register a new Patient account.

**Request Payload:**
```json
{
  "email": "sarah.connor@example.com",
  "password": "Password123!",
  "first_name": "Sarah",
  "last_name": "Connor",
  "date_of_birth": "1985-02-28",
  "gender": "FEMALE",
  "emergency_contact_name": "John Connor",
  "emergency_contact_phone": "+1-555-0199",
  "medical_history": "Positional dizziness after rapid movement"
}
```

**Response (HTTP 201 Created):**
```json
{
  "id": "c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
  "email": "sarah.connor@example.com",
  "first_name": "Sarah",
  "last_name": "Connor",
  "role": "PATIENT",
  "is_active": true,
  "created_at": "2026-08-31T01:00:00Z",
  "patient_profile_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
  "doctor_profile_id": null
}
```

---

### 2. `POST /api/auth/register/doctor`
Register a new Clinician account.

**Request Payload:**
```json
{
  "email": "dr.welby@clinic.org",
  "password": "DoctorPass123!",
  "first_name": "Marcus",
  "last_name": "Welby",
  "specialization": "Neurotology",
  "license_identifier": "LIC-VERT-9921"
}
```

**Response (HTTP 201 Created):**
```json
{
  "id": "e2f3a4b5-c6d7-8e9f-0a1b-2c3d4e5f6a7b",
  "email": "dr.welby@clinic.org",
  "first_name": "Marcus",
  "last_name": "Welby",
  "role": "DOCTOR",
  "is_active": true,
  "created_at": "2026-08-31T01:00:00Z",
  "patient_profile_id": null,
  "doctor_profile_id": "f8e7d6c5-b4a3-2f1e-0d9c-8b7a6f5e4d3c"
}
```

---

### 3. `POST /api/auth/login`
Authenticate user credentials and receive JWT.

**Request Payload:**
```json
{
  "email": "sarah.connor@example.com",
  "password": "Password123!"
}
```

**Response (HTTP 200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
    "email": "sarah.connor@example.com",
    "first_name": "Sarah",
    "last_name": "Connor",
    "role": "PATIENT",
    "is_active": true,
    "created_at": "2026-08-31T01:00:00Z",
    "patient_profile_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
    "doctor_profile_id": null
  }
}
```

---

### 4. `GET /api/auth/me`
Retrieve profile of currently authenticated user.

**Header:**
```http
Authorization: Bearer <access_token>
```

**Response (HTTP 200 OK):**
```json
{
  "id": "c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
  "email": "sarah.connor@example.com",
  "first_name": "Sarah",
  "last_name": "Connor",
  "role": "PATIENT",
  "is_active": true,
  "created_at": "2026-08-31T01:00:00Z",
  "patient_profile_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
  "doctor_profile_id": null
}
```

