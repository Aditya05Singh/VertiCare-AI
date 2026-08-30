import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class NoteType(str, enum.Enum):
    ROUTINE_REVIEW = "ROUTINE_REVIEW"
    EMERGENCY_FOLLOW_UP = "EMERGENCY_FOLLOW_UP"
    DIAGNOSTIC_HYPOTHESIS = "DIAGNOSTIC_HYPOTHESIS"
    DISCHARGE = "DISCHARGE"


class DoctorNote(Base):
    __tablename__ = "doctor_notes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    risk_assessment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("risk_assessments.id", ondelete="SET NULL"), nullable=True
    )
    note_type: Mapped[NoteType] = mapped_column(
        SQLEnum(NoteType, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        default=NoteType.ROUTINE_REVIEW,
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_shared_with_patient: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    patient = relationship("PatientProfile", back_populates="doctor_notes")
    doctor = relationship("DoctorProfile", back_populates="authored_notes")
    risk_assessment = relationship("RiskAssessment", back_populates="doctor_notes")
