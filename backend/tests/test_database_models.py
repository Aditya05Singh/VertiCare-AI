from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.models import Base, User, UserRole, PatientProfile, DoctorProfile, DoctorPatient, Gender

# In-memory test SQLite database
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_user_creation_and_unique_email():
    db = TestingSessionLocal()
    user1 = User(
        email="patient1@example.com",
        password_hash="fakehash123",
        first_name="Jane",
        last_name="Doe",
        role=UserRole.PATIENT
    )
    db.add(user1)
    db.commit()

    assert user1.id is not None
    assert user1.email == "patient1@example.com"
    assert user1.full_name == "Jane Doe"
    assert user1.is_active is True

    # Duplicate email should raise IntegrityError
    user2 = User(
        email="patient1@example.com",
        password_hash="differenthash",
        first_name="Jane",
        last_name="Smith",
        role=UserRole.PATIENT
    )
    db.add(user2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.close()


def test_patient_profile_relationship():
    db = TestingSessionLocal()
    user = User(
        email="patient@example.com",
        password_hash="fakehash",
        first_name="John",
        last_name="Patient",
        role=UserRole.PATIENT
    )
    db.add(user)
    db.flush()

    profile = PatientProfile(
        user_id=user.id,
        date_of_birth=date(1992, 5, 14),
        gender=Gender.MALE,
        emergency_contact_name="Mary Patient",
        emergency_contact_phone="+1234567890",
        medical_history="Mild recurrent dizziness"
    )
    db.add(profile)
    db.commit()

    # Query back
    fetched_user = db.query(User).filter(User.email == "patient@example.com").first()
    assert fetched_user is not None
    assert fetched_user.patient_profile is not None
    assert fetched_user.patient_profile.date_of_birth == date(1992, 5, 14)
    assert fetched_user.patient_profile.user.email == "patient@example.com"
    db.close()


def test_doctor_profile_relationship():
    db = TestingSessionLocal()
    user = User(
        email="doctor@example.com",
        password_hash="fakehash",
        first_name="Alice",
        last_name="Smith",
        role=UserRole.DOCTOR
    )
    db.add(user)
    db.flush()

    profile = DoctorProfile(
        user_id=user.id,
        specialization="Neurotology & Vestibular Disorders",
        license_identifier="MED-998877"
    )
    db.add(profile)
    db.commit()

    fetched_user = db.query(User).filter(User.email == "doctor@example.com").first()
    assert fetched_user is not None
    assert fetched_user.doctor_profile is not None
    assert fetched_user.doctor_profile.license_identifier == "MED-998877"
    db.close()


def test_doctor_patient_assignment_and_uniqueness():
    db = TestingSessionLocal()
    # Create doctor
    doc_user = User(email="doc1@test.com", password_hash="h1", first_name="Dr", last_name="A", role=UserRole.DOCTOR)
    db.add(doc_user)
    db.flush()
    doc_profile = DoctorProfile(user_id=doc_user.id, specialization="ENT", license_identifier="LIC-001")
    db.add(doc_profile)
    db.flush()

    # Create patient
    pat_user = User(email="pat1@test.com", password_hash="h2", first_name="Pat", last_name="B", role=UserRole.PATIENT)
    db.add(pat_user)
    db.flush()
    pat_profile = PatientProfile(user_id=pat_user.id, date_of_birth=date(1990, 1, 1), gender=Gender.FEMALE)
    db.add(pat_profile)
    db.flush()

    # Assign
    assignment = DoctorPatient(doctor_id=doc_profile.id, patient_id=pat_profile.id)
    db.add(assignment)
    db.commit()

    assert assignment.id is not None
    assert len(doc_profile.patient_assignments) == 1
    assert len(pat_profile.doctor_assignments) == 1

    # Duplicate assignment must fail
    dup_assignment = DoctorPatient(doctor_id=doc_profile.id, patient_id=pat_profile.id)
    db.add(dup_assignment)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.close()

