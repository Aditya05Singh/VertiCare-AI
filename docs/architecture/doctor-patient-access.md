# Doctor-Patient Relationship & Patient Record Authorization Architecture

## 1. Architectural Hierarchy & Canonical Identifiers

VertiCare AI enforces a strict role-based data model. The relationships between authentication identities, clinical profiles, and clinical assignments are structured as follows:

```
User (id, email, role, is_active)
 ├── PatientProfile (id, user_id, date_of_birth, gender, emergency_contact_name, ...)
 └── DoctorProfile (id, user_id, specialization, license_identifier, ...)

DoctorPatient (id, doctor_id, patient_id, assigned_at)
 ├── doctor_id → DoctorProfile.id (ForeignKey, Indexed)
 └── patient_id → PatientProfile.id (ForeignKey, Indexed)
     [UniqueConstraint: (doctor_id, patient_id)]
```

### Canonical Identifier Mapping
- **Doctor Canonical ID:** `DoctorProfile.id` (`doctor_id` in `DoctorPatient`)
- **Patient Canonical ID:** `PatientProfile.id` (`patient_id` in `DoctorPatient`)
- **Compatibility Layer:** For frictionless UI experience, API authorization dependencies resolve both `Profile.id` and `User.id` transparently to the canonical `Profile.id` before evaluating relationship constraints.

---

## 2. Centralized Authorization Dependency (`require_doctor_patient_access`)

All clinician-facing patient data endpoints utilize the centralized dependency `require_doctor_patient_access`:

```python
def require_doctor_patient_access(
    patient_id: str,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
) -> PatientProfile:
    doctor_id = current_user.doctor_profile.id

    patient = db.query(PatientProfile).filter(
        (PatientProfile.id == patient_id) | (PatientProfile.user_id == patient_id)
    ).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not assigned to current doctor."
        )

    assignment = db.query(DoctorPatient).filter(
        DoctorPatient.doctor_id == doctor_id,
        DoctorPatient.patient_id == patient.id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not assigned to current doctor."
        )

    return patient
```

### Security Guarantees:
1. **Role Verification:** Requester must be authenticated with role `DOCTOR` and have an active `DoctorProfile`.
2. **Patient Resolution:** Resolves target patient by `PatientProfile.id` or `User.id`.
3. **Mutual Assignment Check:** Verifies active `DoctorPatient` assignment linking `(doctor_profile.id, patient_profile.id)`.
4. **Anti-IDOR Protection:** If a patient is unassigned or does not exist, the API unconditionally returns `404 Not Found` with a standardized detail message, preventing attackers from discovering whether arbitrary patient IDs exist in the system.
5. **Privacy Protection:** Patient responses never include password hashes, JWTs, or backend system secrets.

---

## 3. Patient Record Clinical Scope

Authorized clinicians have access to the complete multimodal monitoring record for assigned patients:
- **Patient Overview Dossier:** Demographic information, emergency contacts, latest monitoring summaries across modalities.
- **Daily Health History:** Longitudinal daily symptom logs (dizziness severity, imbalance severity, sleep, stress, medication adherence, triggers).
- **Health Trends:** Multi-day symptom rolling averages and lifestyle correlations.
- **Questionnaire Sessions:** Adaptive screening session responses and answers.
- **Eye Movement Screening:** Computer-vision tracking quality, numerical kinematic features, and evidence-based AI screening interpretation.
- **AI Risk Assessments:** Longitudinal XGBoost risk tier assessments and contributing factors.
- **Clinical Decision Support Notes:** Clinician-authored progress and assessment notes.
- **Consolidated Clinical Reports:** Multi-modal longitudinal export summary.
- **Emergency Events:** Emergency assistance requests, status transitions, and clinician acknowledgment logs.

