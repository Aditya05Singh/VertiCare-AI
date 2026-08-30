import enum
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Date, Text, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[Gender] = mapped_column(
        SQLEnum(Gender, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        default=Gender.PREFER_NOT_TO_SAY,
        nullable=False
    )
    medical_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    doctor_assignments = relationship(
        "DoctorPatient",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
    daily_health_checks = relationship(
        "DailyHealthCheck",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
    questionnaire_sessions = relationship(
        "QuestionnaireSession",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
    eye_analysis_sessions = relationship(
        "EyeAnalysisSession",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
    risk_assessments = relationship(
        "RiskAssessment",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
    doctor_notes = relationship(
        "DoctorNote",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
    emergency_events = relationship(
        "EmergencyEvent",
        back_populates="patient",
        cascade="all, delete-orphan"
    )


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    specialization: Mapped[str] = mapped_column(
        String(150), nullable=False, default="Otolaryngology / Neurotology"
    )
    license_identifier: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    patient_assignments = relationship(
        "DoctorPatient",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )
    authored_notes = relationship(
        "DoctorNote",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )


class DoctorPatient(Base):
    __tablename__ = "doctor_patients"
    __table_args__ = (
        UniqueConstraint("doctor_id", "patient_id", name="uq_doctor_patient_assignment"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    doctor_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    doctor = relationship("DoctorProfile", back_populates="patient_assignments")
    patient = relationship("PatientProfile", back_populates="doctor_assignments")
