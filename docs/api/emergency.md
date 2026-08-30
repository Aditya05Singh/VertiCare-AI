# Emergency Support API Specification

This document details the REST API endpoints under `/api/emergency-events` for patient emergency support, contact workflows, and clinician triage.

---

## 1. Endpoints Overview

| Method | Endpoint | Authorized Roles | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/emergency-events/guidance` | Public / Authenticated | Retrieves static, non-diagnostic safety guidelines. |
| `GET` | `/api/emergency-events/context` | `PATIENT` | Retrieves emergency metadata (contact info, assigned doctor, active event). |
| `POST` | `/api/emergency-events` | `PATIENT` | Creates a new emergency support event. |
| `GET` | `/api/emergency-events` | `PATIENT`, `DOCTOR` | Lists emergency events (patient's own or doctor's assigned cohort). |
| `GET` | `/api/emergency-events/{id}` | `PATIENT`, `DOCTOR` | Retrieves details for an authorized emergency event. |
| `POST` | `/api/emergency-events/{id}/patient-action` | `PATIENT` | Executes patient action (`CONTACT_DOCTOR`, `CONTACT_EMERGENCY_CONTACT`, `CANCEL`). |
| `POST` | `/api/emergency-events/{id}/doctor-action` | `DOCTOR` | Executes clinician transition (`ACKNOWLEDGE`, `RESOLVE`). |

---

## 2. Request & Response Payloads

### 2.1 `GET /api/emergency-events/context`
Returns contextual information for the patient emergency support view.

**Response (HTTP 200 OK):**
```json
{
  "has_emergency_contact": true,
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+1-555-0144",
  "has_assigned_doctor": true,
  "assigned_doctor_name": "Dr. Marcus Welby",
  "assigned_doctor_specialization": "Neurotology",
  "latest_risk_level": "HIGH",
  "latest_risk_score": 0.78,
  "latest_risk_assessment_id": "assessment-uuid-1",
  "active_event": null
}
```

---

### 2.2 `POST /api/emergency-events`
Creates an emergency support event.

**Request Payload:**
```json
{
  "severity": "HIGH",
  "risk_assessment_id": "assessment-uuid-1",
  "notes": "Sudden rotational vertigo while standing.",
  "initiate_doctor_contact": true,
  "initiate_emergency_contact": false
}
```

**Response (HTTP 201 Created):**
```json
{
  "id": "event-uuid-1",
  "patient_id": "patient-uuid-1",
  "patient_name": "Alice Smith",
  "patient_dob": "1988-04-12",
  "patient_gender": "FEMALE",
  "risk_assessment_id": "assessment-uuid-1",
  "risk_level": "HIGH",
  "risk_score": 0.78,
  "severity": "HIGH",
  "status": "CONTACT_INITIATED",
  "contacted_doctor": true,
  "contacted_emergency_contact": false,
  "contacted_at": "2026-08-31T01:50:00Z",
  "notes": "Sudden rotational vertigo while standing.",
  "created_at": "2026-08-31T01:50:00Z",
  "updated_at": "2026-08-31T01:50:00Z",
  "assigned_doctor_name": "Dr. Marcus Welby",
  "assigned_doctor_specialization": "Neurotology",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+1-555-0144",
  "notice": "Emergency support and escalation workflow. This is NOT an automatic diagnosis or emergency dispatch service."
}
```

---

### 2.3 `POST /api/emergency-events/{id}/patient-action`
Executes an authorized patient action on their active emergency event.

**Request Payload:**
```json
{
  "action": "CONTACT_DOCTOR",
  "notes": "Requesting immediate clinician phone review."
}
```

---

### 2.4 `POST /api/emergency-events/{id}/doctor-action`
Executes an authorized clinician status transition on an assigned patient's event.

**Request Payload:**
```json
{
  "action": "RESOLVE",
  "notes": "Spoke with patient by phone. Advised bed rest and scheduled follow-up."
}
```

---

## 3. Communication Service Disclosure

> [!NOTE]
> This application does not include an external SMS gateway, telephony dispatch, or push notification provider. All contact actions are accurately tracked in the audit trail without claiming external delivery success.

