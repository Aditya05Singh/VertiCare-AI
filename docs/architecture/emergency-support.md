# Emergency Support & Escalation Workflow Architecture

This document describes the architectural design, safety boundaries, state machine, and authorization model of the VertiCare AI Emergency Support System.

---

## 1. Architectural Purpose & Medical Safety Boundaries

```
             Patient Experience High / Acute Symptoms
                               │
                               ▼
                [Emergency Support Portal]
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
   [Contact Assigned Doctor]          [Contact Emergency Contact]
            │                                     │
            ▼                                     ▼
  [Create/Update EmergencyEvent]       [Record Event + Device Call]
            │                                     │
            └──────────────────┬──────────────────┘
                               │
                               ▼
                   [Clinician Alert Triage]
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
    [Mark Acknowledged]                    [Mark Resolved]
```

> [!CAUTION]
> **Prototype Safety Boundary**
>
> 1. **Support & Escalation Only:** VertiCare AI provides an emergency *support and escalation workflow*, **not** an automated diagnostic engine or emergency dispatch provider.
> 2. **No False Delivery Claims:** Because no external SMS/telephony provider is integrated, the system explicitly records contact actions and instructs the user: *"Your request has been recorded. Please use the available contact method to reach your doctor."*
> 3. **Non-Diagnostic Language:** The system never declares "stroke detected", "BPPV emergency confirmed", or "disease confirmed". It presents neutral, safety-first directions.
> 4. **No Fabricated Phone Numbers:** Contact information is drawn strictly from configured `PatientProfile` data and assigned doctor relationships.

---

## 2. Emergency Event State Machine

All emergency events follow a deterministic state transition lifecycle:

```
                  ┌───────────────┐
                  │    PENDING    │
                  └───────┬───────┘
                          │
          ┌───────────────┼───────────────┐
          │ (Initiate     │ (Doctor Ack)  │ (Cancel)
          ▼  Contact)     ▼               ▼
  ┌─────────────────┐ ┌───────────────┐ ┌───────────────┐
  │CONTACT_INITIATED│ │ ACKNOWLEDGED  │ │   CANCELLED   │ (Terminal)
  └───────┬─────────┘ └───────┬───────┘ └───────────────┘
          │ (Doctor Ack)      │ (Doctor Resolve)
          ▼                   ▼
  ┌───────────────┐   ┌───────────────┐
  │ ACKNOWLEDGED  │──▶│   RESOLVED    │ (Terminal)
  └───────────────┘   └───────────────┘
```

### Transition Matrix:

| Current Status | Allowed Transitions | Triggering Role |
| :--- | :--- | :--- |
| `PENDING` | `CONTACT_INITIATED`, `ACKNOWLEDGED`, `RESOLVED`, `CANCELLED` | Patient / Assigned Doctor |
| `CONTACT_INITIATED` | `ACKNOWLEDGED`, `RESOLVED`, `CANCELLED` | Patient (Cancel) / Assigned Doctor |
| `ACKNOWLEDGED` | `RESOLVED`, `CANCELLED` | Patient (Cancel) / Assigned Doctor |
| `RESOLVED` | *(Terminal — no transitions permitted)* | None |
| `CANCELLED` | *(Terminal — no transitions permitted)* | None |

---

## 3. Data Model & Database Architecture

### `EmergencyEvent` Entity:
- **`id`**: String(36) UUID Primary Key.
- **`patient_id`**: String(36) Foreign Key (`patient_profiles.id`, ondelete='CASCADE'), Indexed.
- **`risk_assessment_id`**: String(36) Foreign Key (`risk_assessments.id`, ondelete='SET NULL'), Nullable, Indexed.
- **`severity`**: Enum (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), Indexed.
- **`status`**: Enum (`PENDING`, `CONTACT_INITIATED`, `ACKNOWLEDGED`, `RESOLVED`, `CANCELLED`), Indexed.
- **`contacted_doctor`**: Boolean, Default `False`.
- **`contacted_emergency_contact`**: Boolean, Default `False`.
- **`contacted_at`**: DateTime (UTC), Nullable.
- **`notes`**: Text, Nullable (contains symptom notes and clinician triage history).
- **`created_at`**: DateTime (UTC), Indexed.
- **`updated_at`**: DateTime (UTC).

---

## 4. Authorization & Anti-IDOR Security

```
                 Incoming Emergency Request
                             │
                             ▼
               [JWT Authentication Verified]
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
     Patient Requester                 Doctor Requester
            │                                 │
            ▼                                 ▼
   [Event Patient ID ==             [Patient ID Assigned in
    User Patient Profile ID]         DoctorPatient Table]
            │                                 │
            ├───────────────┬─────────────────┤
            ▼               ▼                 ▼
          MATCH          NO MATCH          NO MATCH
            │               │                 │
            ▼               ▼                 ▼
       HTTP 200/201      HTTP 404          HTTP 404
      Access Granted    (Anti-IDOR)       (Anti-IDOR)
```

- **Patient Isolation:** A patient can only view, create, or update emergency events linked to their own `patient_profile.id`.
- **Doctor Assignment Restriction:** A clinician can only view and manage emergency events for patients linked to them via active `DoctorPatient` records.
- **Anti-IDOR Protection:** Cross-tenant or unassigned requests return **`HTTP 404 Not Found`** to prevent leaking event or patient existence.

