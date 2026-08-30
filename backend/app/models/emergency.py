import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EmergencySeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EmergencyStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONTACT_INITIATED = "CONTACT_INITIATED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class EmergencyEvent(Base):
    __tablename__ = "emergency_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    risk_assessment_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("risk_assessments.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    severity: Mapped[EmergencySeverity] = mapped_column(
        SQLEnum(
            EmergencySeverity,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=EmergencySeverity.HIGH,
        nullable=False,
        index=True
    )
    status: Mapped[EmergencyStatus] = mapped_column(
        SQLEnum(
            EmergencyStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=EmergencyStatus.PENDING,
        nullable=False,
        index=True
    )
    contacted_doctor: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    contacted_emergency_contact: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    contacted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    patient = relationship("PatientProfile", back_populates="emergency_events")
    risk_assessment = relationship("RiskAssessment", back_populates="emergency_events")
