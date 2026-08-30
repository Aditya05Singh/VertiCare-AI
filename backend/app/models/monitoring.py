import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, Text, Date, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DailyHealthCheck(Base):
    __tablename__ = "daily_health_checks"
    __table_args__ = (
        UniqueConstraint("patient_id", "check_date", name="uq_patient_daily_health_check"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    check_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Core Vestibular Symptom Severity (0–10 scale)
    dizziness_severity: Mapped[int] = mapped_column(Integer, nullable=False)
    episode_duration: Mapped[str] = mapped_column(String(100), nullable=False, default="None / Subsided")
    imbalance_severity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Associated Symptoms
    nausea: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    headache: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Lifestyle & Biometrics
    sleep_hours: Mapped[float] = mapped_column(Float, nullable=False)
    hydration_level: Mapped[str] = mapped_column(String(50), nullable=False, default="Moderate (1-2L)")
    stress_level: Mapped[int] = mapped_column(Integer, nullable=False)

    # Medication & Environmental Triggers
    medication_adherence: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Taken as prescribed"
    )
    triggers: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationship
    patient = relationship("PatientProfile", back_populates="daily_health_checks")
