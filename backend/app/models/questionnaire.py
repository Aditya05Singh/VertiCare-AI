import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class QuestionType(str, enum.Enum):
    BOOLEAN = "BOOLEAN"
    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTI_CHOICE = "MULTI_CHOICE"
    NUMBER = "NUMBER"
    TEXT = "TEXT"


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class QuestionnaireQuestion(Base):
    __tablename__ = "questionnaire_questions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    question_code: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    version: Mapped[str] = mapped_column(String(20), default="v1.0", nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        SQLEnum(QuestionType, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    options: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    branching_rules: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    answers = relationship("QuestionnaireAnswer", back_populates="question")


class QuestionnaireSession(Base):
    __tablename__ = "questionnaire_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    version: Mapped[str] = mapped_column(String(20), default="v1.0", nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[SessionStatus] = mapped_column(
        SQLEnum(SessionStatus, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        default=SessionStatus.IN_PROGRESS,
        index=True,
        nullable=False
    )
    current_question_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    patient = relationship("PatientProfile", back_populates="questionnaire_sessions")
    answers = relationship(
        "QuestionnaireAnswer",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="QuestionnaireAnswer.answered_at"
    )


class QuestionnaireAnswer(Base):
    __tablename__ = "questionnaire_answers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questionnaire_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questionnaire_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    answer: Mapped[dict | list | str | int | float | bool] = mapped_column(
        JSON, nullable=False
    )
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Relationships
    session = relationship("QuestionnaireSession", back_populates="answers")
    question = relationship("QuestionnaireQuestion", back_populates="answers")
