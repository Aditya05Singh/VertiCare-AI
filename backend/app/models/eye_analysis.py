import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EyeAnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INSUFFICIENT_QUALITY = "INSUFFICIENT_QUALITY"
    CANCELLED = "CANCELLED"


class EyeAnalysisSession(Base):
    __tablename__ = "eye_analysis_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    analysis_status: Mapped[EyeAnalysisStatus] = mapped_column(
        SQLEnum(EyeAnalysisStatus, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        default=EyeAnalysisStatus.PENDING,
        index=True,
        nullable=False
    )
    quality_summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    screening_result: Mapped[dict | None] = mapped_column(JSON, default=dict, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    patient = relationship("PatientProfile", back_populates="eye_analysis_sessions")
    features = relationship(
        "EyeMovementFeature",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="EyeMovementFeature.feature_name"
    )


class EyeMovementFeature(Base):
    __tablename__ = "eye_movement_features"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("eye_analysis_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    feature_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    feature_value: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Relationships
    session = relationship("EyeAnalysisSession", back_populates="features")
