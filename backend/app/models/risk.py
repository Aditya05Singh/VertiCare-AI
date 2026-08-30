import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    health_check_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("daily_health_checks.id", ondelete="SET NULL"),
        nullable=True
    )
    questionnaire_session_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("questionnaire_sessions.id", ondelete="SET NULL"),
        nullable=True
    )
    eye_analysis_session_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("eye_analysis_sessions.id", ondelete="SET NULL"),
        nullable=True
    )
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        SQLEnum(RiskLevel, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    contributing_factors: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False, index=True
    )

    # Relationships
    patient = relationship("PatientProfile", back_populates="risk_assessments")
    health_check = relationship("DailyHealthCheck")
    questionnaire_session = relationship("QuestionnaireSession")
    eye_analysis_session = relationship("EyeAnalysisSession")
    doctor_notes = relationship("DoctorNote", back_populates="risk_assessment")
    emergency_events = relationship("EmergencyEvent", back_populates="risk_assessment")
