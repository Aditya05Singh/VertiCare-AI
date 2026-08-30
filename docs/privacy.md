# Privacy and Data Protection Specification

## 1. Overview
VertiCare AI is designed as a privacy-preserving clinical decision support and vertigo monitoring platform. Patient health information (PHI) and biometric sensor streams are handled in strict compliance with data minimization, purpose limitation, and storage limitation principles.

## 2. Biometric and Computer Vision Privacy
- **Zero Raw Video Storage:** Consumer webcam video streams are processed purely in real-time in the client/runtime context. Raw video frames are discarded immediately after eye coordinate/landmark extraction.
- **Parametric Feature Storage Only:** Only aggregated kinematic numerical features (such as horizontal/vertical mean velocity, blink rate, and direction change counts) and screening status representations are persisted.
- **Client-Side Permission:** Explicit camera permission is requested via standard HTML5 `getUserMedia` APIs, and the user retains active control to stop the camera stream at any point.

## 3. Credential & Authentication Privacy
- **Secure Password Hashing:** Passwords are never stored in plaintext and are hashed using bcrypt with salt rounds before database persistence.
- **Token Security:** JWT tokens contain only non-sensitive claims (`sub`: User UUID, `role`: PATIENT/DOCTOR, `email`) and never include medical history, questionnaire answers, or clinical notes.
- **Zero Secrets in Frontend:** API keys, database credentials, and secret signing keys are kept strictly on the backend environment.

## 4. Tenant Isolation & Access Control
- **Anti-IDOR Protection:** Backend route dependencies (`require_patient`, `require_doctor`, `require_doctor_patient_access`) enforce strict relational ownership at the database level.
- **Patient Isolation:** A patient can only view, query, and modify their own health checks, questionnaires, eye analysis sessions, and risk assessments.
- **Clinician Boundary:** Clinicians can only access records for patients who have an active clinical relationship (`DoctorPatient` table).

## 5. Auditability and Data Deletion
- Cascading delete constraints ensure that when a patient profile is purged, associated daily monitoring logs, questionnaire answers, and risk records are removed cleanly.

