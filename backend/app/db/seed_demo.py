import uuid
from datetime import datetime, date, timezone, timedelta
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.profile import DoctorProfile, PatientProfile, DoctorPatient, Gender
from app.models.monitoring import DailyHealthCheck
from app.models.clinical import DoctorNote, NoteType
from app.models.risk import RiskAssessment, RiskLevel
from app.core.security import hash_password
from app.core.logging import logger


def seed_demo_accounts():
    """
    Seeds demo clinician and patient accounts with rich sample data so that
    both the Patient Portal and Doctor Dashboard work immediately out of the box.
    """
    db = SessionLocal()
    try:
        # 1. Seed or update Demo Doctor
        doc_email = "doctor@verticare.org"
        doc_user = db.query(User).filter(User.email == doc_email).first()

        if not doc_user:
            doc_user = User(
                email=doc_email,
                password_hash=hash_password("Doctor123!"),
                first_name="Sarah",
                last_name="Jenkins, MD",
                role=UserRole.DOCTOR,
                is_active=True
            )
            db.add(doc_user)
            db.flush()

            doc_profile = DoctorProfile(
                user_id=doc_user.id,
                specialization="Neurotology & Vestibular Medicine",
                license_identifier="LIC-MD-98421"
            )
            db.add(doc_profile)
            db.flush()
            logger.info(f"Seeded demo doctor account: {doc_email}")
        else:
            doc_profile = doc_user.doctor_profile

        # 2. Seed or ensure Demo Patient (demo@verticare.org)
        demo_email = "demo@verticare.org"
        demo_user = db.query(User).filter(User.email == demo_email).first()

        if not demo_user:
            demo_user = User(
                email=demo_email,
                password_hash=hash_password("Password123!"),
                first_name="Demo",
                last_name="Patient",
                role=UserRole.PATIENT,
                is_active=True
            )
            db.add(demo_user)
            db.flush()

            demo_profile = PatientProfile(
                user_id=demo_user.id,
                date_of_birth=date(1990, 5, 14),
                gender=Gender.FEMALE,
                medical_history="Mild recurrent vestibular symptoms under clinical observation."
            )
            db.add(demo_profile)
            db.flush()
            logger.info(f"Seeded demo patient account: {demo_email}")
        else:
            demo_profile = demo_user.patient_profile

        # Assign demo patient to demo doctor
        if demo_profile and doc_profile:
            assign = db.query(DoctorPatient).filter(
                DoctorPatient.doctor_id == doc_profile.id,
                DoctorPatient.patient_id == demo_profile.id
            ).first()
            if not assign:
                db.add(DoctorPatient(doctor_id=doc_profile.id, patient_id=demo_profile.id))

        # 3. Seed Patient 2: Robert Chen (Medium Risk / BPPV)
        pat2_email = "robert.chen@verticare.org"
        pat2_user = db.query(User).filter(User.email == pat2_email).first()
        if not pat2_user and doc_profile:
            pat2_user = User(
                email=pat2_email,
                password_hash=hash_password("Patient123!"),
                first_name="Robert",
                last_name="Chen",
                role=UserRole.PATIENT,
                is_active=True
            )
            db.add(pat2_user)
            db.flush()

            pat2_profile = PatientProfile(
                user_id=pat2_user.id,
                date_of_birth=date(1978, 6, 15),
                gender=Gender.MALE,
                medical_history="Episodic positional vertigo provoked by rolling in bed or tilting head back."
            )
            db.add(pat2_profile)
            db.flush()

            db.add(DoctorPatient(doctor_id=doc_profile.id, patient_id=pat2_profile.id))

            db.add(DailyHealthCheck(
                patient_id=pat2_profile.id,
                check_date=date.today(),
                dizziness_severity=6,
                imbalance_severity=5,
                episode_duration="< 1 minute",
                nausea=True,
                headache=False,
                sleep_hours=7.0,
                hydration_level="Moderate (1-2L)",
                stress_level=4,
                triggers=["turning_in_bed", "looking_up_bending"],
                notes="Transient intense spinning upon awakening when rolling to right side."
            ))

            db.add(RiskAssessment(
                patient_id=pat2_profile.id,
                risk_level=RiskLevel.MEDIUM,
                risk_score=58.5,
                model_name="verticare-multimodal-risk-engine",
                model_version="1.0.0",
                contributing_factors=[
                    "Positional trigger pattern with brief episodic duration (<1 min)",
                    "Elevated horizontal slow-phase eye velocity on rightward head tilt",
                    "Absence of focal neurological red flags"
                ]
            ))

        # 4. Seed Patient 3: Elena Rostova (High Risk / Triage Alert)
        pat3_email = "elena.rostova@verticare.org"
        pat3_user = db.query(User).filter(User.email == pat3_email).first()
        if not pat3_user and doc_profile:
            pat3_user = User(
                email=pat3_email,
                password_hash=hash_password("Patient123!"),
                first_name="Elena",
                last_name="Rostova",
                role=UserRole.PATIENT,
                is_active=True
            )
            db.add(pat3_user)
            db.flush()

            pat3_profile = PatientProfile(
                user_id=pat3_user.id,
                date_of_birth=date(1964, 11, 20),
                gender=Gender.FEMALE,
                medical_history="Acute continuous spontaneous vertigo for 24+ hours with severe gait ataxia."
            )
            db.add(pat3_profile)
            db.flush()

            db.add(DoctorPatient(doctor_id=doc_profile.id, patient_id=pat3_profile.id))

            db.add(DailyHealthCheck(
                patient_id=pat3_profile.id,
                check_date=date.today(),
                dizziness_severity=9,
                imbalance_severity=9,
                episode_duration="Days / Constant",
                nausea=True,
                headache=True,
                sleep_hours=4.0,
                hydration_level="Low (<1L)",
                stress_level=8,
                triggers=["spontaneous_no_trigger"],
                notes="Constant severe rotational vertigo and persistent nausea. Requires assistance walking."
            ))

            risk_3 = RiskAssessment(
                patient_id=pat3_profile.id,
                risk_level=RiskLevel.HIGH,
                risk_score=86.0,
                model_name="verticare-multimodal-risk-engine",
                model_version="1.0.0",
                contributing_factors=[
                    "Acute spontaneous continuous vertigo lasting >24 hours",
                    "Severe gait ataxia and inability to ambulate safely",
                    "Elevated ocular drift with high-velocity horizontal jerk pattern"
                ]
            )
            db.add(risk_3)
            db.flush()

            db.add(DoctorNote(
                doctor_id=doc_profile.id,
                patient_id=pat3_profile.id,
                risk_assessment_id=risk_3.id,
                note_type=NoteType.DIAGNOSTIC_HYPOTHESIS,
                content=(
                    "Initial Tele-Triage Review: Patient presents with Acute Vestibular Syndrome (AVS). "
                    "Differential diagnosis includes acute peripheral vestibular neuritis vs cerebellar/brainstem "
                    "posterior circulation ischemic stroke. Bedside HINTS exam protocol scheduled for urgent clinic evaluation."
                ),
                is_shared_with_patient=True
            ))

        db.commit()
        logger.info("Demo accounts and clinical records successfully seeded.")
    except Exception as e:
        db.rollback()
        logger.warning(f"Error seeding demo accounts: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_accounts()

