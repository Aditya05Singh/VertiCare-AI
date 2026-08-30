# Database Schema — Step 3 Foundation

This document specifies the relational database schema implemented for user management, profiles, and clinician-patient associations.

---

## Entity-Relationship Diagram

```
User (1) ────── (1) PatientProfile (1) ────── (N) DoctorPatient (N) ────── (1) DoctorProfile (1) ────── (1) User
```

---

## Tables Specification

### 1. `users`
Core authentication and user identity store.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Normalized lower-case email |
| `password_hash` | VARCHAR(255) | NOT NULL | Salted bcrypt hash |
| `first_name` | VARCHAR(100) | NOT NULL | User first name |
| `last_name` | VARCHAR(100) | NOT NULL | User last name |
| `role` | ENUM ('PATIENT', 'DOCTOR') | NOT NULL, INDEX | Role-based authorization |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Active account flag |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Timestamp of creation |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Timestamp of last update |

### 2. `patient_profiles`
Clinical profile linked 1:1 to a `User` with role `PATIENT`.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `user_id` | VARCHAR(36) | FK -> `users.id` (CASCADE), UNIQUE, INDEX | Linked user identity |
| `date_of_birth` | DATE | NOT NULL | Patient date of birth |
| `gender` | ENUM ('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY') | NOT NULL | Gender identity |
| `medical_history` | TEXT | NULLABLE | Self-reported medical history |
| `emergency_contact_name` | VARCHAR(100) | NULLABLE | Emergency contact person |
| `emergency_contact_phone` | VARCHAR(30) | NULLABLE | Emergency contact phone number |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record update timestamp |

### 3. `doctor_profiles`
Professional credentials linked 1:1 to a `User` with role `DOCTOR`.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `user_id` | VARCHAR(36) | FK -> `users.id` (CASCADE), UNIQUE, INDEX | Linked clinician user |
| `specialization` | VARCHAR(150) | NOT NULL | Clinical specialty (e.g. Otolaryngology) |
| `license_identifier` | VARCHAR(100) | UNIQUE, INDEX, NOT NULL | Medical registration/license number |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record update timestamp |

### 4. `doctor_patients`
Associative junction table linking clinicians to assigned patients.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `doctor_id` | VARCHAR(36) | FK -> `doctor_profiles.id` (CASCADE), INDEX | Assigned doctor |
| `patient_id` | VARCHAR(36) | FK -> `patient_profiles.id` (CASCADE), INDEX | Assigned patient |
| `assigned_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Assignment timestamp |

*Constraint:* `UNIQUE(doctor_id, patient_id)` prevents duplicate assignment pairs.

---

### 5. `daily_health_checks`
Longitudinal daily vestibular symptom, biometrics, and trigger monitoring logs.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `patient_id` | VARCHAR(36) | FK -> `patient_profiles.id` (CASCADE), INDEX | Linked patient identity |
| `check_date` | DATE | NOT NULL, INDEX | Calendar check-in date |
| `dizziness_severity` | INTEGER | NOT NULL | Subjective spinning/vertigo severity (0–10) |
| `episode_duration` | VARCHAR(100) | NOT NULL | Episode time category |
| `imbalance_severity` | INTEGER | NOT NULL | Postural unsteadiness / equilibrium loss (0–10) |
| `nausea` | BOOLEAN | NOT NULL, DEFAULT FALSE | Presence of nausea or gastrointestinal distress |
| `headache` | BOOLEAN | NOT NULL, DEFAULT FALSE | Presence of headache or migraine symptoms |
| `sleep_hours` | FLOAT | NOT NULL | Rest duration (0.0 to 24.0 hours) |
| `hydration_level` | VARCHAR(50) | NOT NULL | Fluid intake estimate |
| `stress_level` | INTEGER | NOT NULL | Subjective psychological tension (0–10) |
| `medication_adherence` | VARCHAR(100) | NOT NULL | Medication compliance status |
| `triggers` | JSON | NOT NULL, DEFAULT '[]' | Recognized environmental/physical triggers list |
| `notes` | TEXT | NULLABLE | Freeform user observations |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record update timestamp |

*Constraint:* `UNIQUE(patient_id, check_date)` strictly guarantees one daily health check log per patient per calendar day. Subsequent logs on the same date update the existing record.

---

### 6. `questionnaire_questions`
Controlled question bank definition store for the adaptive screening flow.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `question_code` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Stable identifier (e.g. `Q_SPINNING`) |
| `version` | VARCHAR(20) | NOT NULL, DEFAULT 'v1.0' | Question bank version tag |
| `question_text` | TEXT | NOT NULL | Human-readable non-diagnostic question |
| `question_type` | ENUM ('BOOLEAN', 'SINGLE_CHOICE', 'MULTI_CHOICE', 'NUMBER', 'TEXT') | NOT NULL | Input type expectation |
| `category` | VARCHAR(100) | NOT NULL | Symptom category grouping |
| `options` | JSON | NOT NULL, DEFAULT '[]' | Choice options array |
| `branching_rules` | JSON | NOT NULL, DEFAULT '{}' | Deterministic branching state machine rules |
| `display_order` | INTEGER | NOT NULL, DEFAULT 0 | Ordering index |
| `active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Active toggle |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Update timestamp |

---

### 7. `questionnaire_sessions`
Patient screening assessment lifecycle tracking.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `patient_id` | VARCHAR(36) | FK -> `patient_profiles.id` (CASCADE), INDEX | Patient owner |
| `version` | VARCHAR(20) | NOT NULL, DEFAULT 'v1.0' | Assessment version |
| `started_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Session start timestamp |
| `completed_at` | TIMESTAMPTZ | NULLABLE | Session completion timestamp |
| `status` | ENUM ('IN_PROGRESS', 'COMPLETED', 'ABANDONED') | NOT NULL, INDEX | Current state |
| `current_question_code` | VARCHAR(50) | NULLABLE | Active question code |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record update timestamp |

---

### 8. `questionnaire_answers`
Patient responses captured during adaptive assessment.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `session_id` | VARCHAR(36) | FK -> `questionnaire_sessions.id` (CASCADE), INDEX | Linked session |
| `question_id` | VARCHAR(36) | FK -> `questionnaire_questions.id` (CASCADE), INDEX | Linked question definition |
| `question_code` | VARCHAR(50) | NOT NULL, INDEX | Denormalized question code |
| `answer` | JSON | NOT NULL | User answer value (bool, str, list, number) |
| `answered_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Answer timestamp |

---

### 9. `eye_analysis_sessions`
Computer-vision eye movement screening assessment sessions.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `patient_id` | VARCHAR(36) | FK -> `patient_profiles.id` (CASCADE), INDEX | Patient owner |
| `started_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Screening session start timestamp |
| `ended_at` | TIMESTAMPTZ | NULLABLE | Screening session end timestamp |
| `analysis_status` | ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'INSUFFICIENT_QUALITY', 'CANCELLED') | NOT NULL, INDEX | Processing/quality status |
| `quality_summary` | JSON | NOT NULL, DEFAULT '{}' | Technical tracking quality indicators |
| `screening_result` | JSON | NULLABLE, DEFAULT '{}' | Evidence-based kinematic screening interpretation |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record update timestamp |

---

### 10. `eye_movement_features`
Derived kinematic numerical features extracted from webcam video stream.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `session_id` | VARCHAR(36) | FK -> `eye_analysis_sessions.id` (CASCADE), INDEX | Linked eye session |
| `feature_name` | VARCHAR(100) | NOT NULL, INDEX | Whitelisted feature name |
| `feature_value` | FLOAT | NOT NULL | Finite numerical metric value |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record creation timestamp |

---

### 11. `risk_assessments`
AI-assisted multimodal vestibular screening risk evaluation records.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `patient_id` | VARCHAR(36) | FK -> `patient_profiles.id` (CASCADE), INDEX | Patient owner |
| `health_check_id` | VARCHAR(36) | FK -> `daily_health_checks.id` (SET NULL), NULLABLE | Associated daily log |
| `questionnaire_session_id` | VARCHAR(36) | FK -> `questionnaire_sessions.id` (SET NULL), NULLABLE | Associated questionnaire |
| `eye_analysis_session_id` | VARCHAR(36) | FK -> `eye_analysis_sessions.id` (SET NULL), NULLABLE | Associated eye analysis |
| `risk_score` | FLOAT | NOT NULL | Calibrated risk score [0.0, 1.0] |
| `risk_level` | ENUM ('LOW', 'MEDIUM', 'HIGH') | NOT NULL, INDEX | Screening risk category |
| `model_name` | VARCHAR(100) | NOT NULL | Model algorithm |
| `model_version` | VARCHAR(50) | NOT NULL | Model artifact version (e.g. `verticare-risk-v1`) |
| `contributing_factors` | JSON | NOT NULL, DEFAULT '[]' | Top explainable contributing observations |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW(), INDEX | Assessment timestamp |

---

### 12. `doctor_notes`
Clinician clinical observations and monitoring notes for assigned patients.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `doctor_id` | VARCHAR(36) | FK -> `doctor_profiles.id` (CASCADE), INDEX | Authoring clinician |
| `patient_id` | VARCHAR(36) | FK -> `patient_profiles.id` (CASCADE), INDEX | Target assigned patient |
| `risk_assessment_id` | VARCHAR(36) | FK -> `risk_assessments.id` (SET NULL), NULLABLE | Optional linked risk assessment |
| `note_type` | ENUM ('GENERAL', 'CLINICAL_OBSERVATION', 'FOLLOW_UP', 'TRIAGE') | NOT NULL | Categorical note classification |
| `content` | TEXT | NOT NULL | Note content text |
| `is_shared_with_patient` | BOOLEAN | NOT NULL, DEFAULT TRUE | Patient visibility permission |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last edit timestamp |

---

### 13. `emergency_events`
Acute red-flag escalation events and clinician review audits.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string identifier |
| `patient_id` | VARCHAR(36) | FK -> `patient_profiles.id` (CASCADE), INDEX | Patient owner |
| `risk_assessment_id` | VARCHAR(36) | FK -> `risk_assessments.id` (SET NULL), NULLABLE | Optional linked risk record |
| `severity` | ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') | NOT NULL, INDEX | Triage urgency tier |
| `status` | ENUM ('PENDING', 'CONTACT_INITIATED', 'ACKNOWLEDGED', 'RESOLVED', 'CANCELLED') | NOT NULL, INDEX | Event lifecycle status |
| `contacted_doctor` | BOOLEAN | NOT NULL, DEFAULT FALSE | Clinician notification state |
| `contacted_emergency_contact` | BOOLEAN | NOT NULL, DEFAULT FALSE | Emergency contact state |
| `contacted_at` | TIMESTAMPTZ | NULLABLE | Escalation initiation timestamp |
| `notes` | TEXT | NULLABLE | Resolution or triage notes |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW(), INDEX | Event creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |






