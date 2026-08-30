from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.questionnaire import (
    QuestionnaireQuestion,
    QuestionnaireSession,
    QuestionnaireAnswer,
    SessionStatus
)
from app.services.questionnaire_engine import QuestionnaireEngine
from app.schemas.questionnaire import (
    QuestionResponse,
    QuestionOption,
    AnswerSubmitRequest,
    SessionProgress,
    SessionResponse,
    AnswerSummaryItem,
    SessionSummaryResponse
)


class QuestionnaireService:
    @classmethod
    def start_or_resume_session(
        cls,
        db: Session,
        patient_id: str
    ) -> SessionResponse:
        """Start a new questionnaire session or resume an active IN_PROGRESS session for the patient."""
        # Ensure question bank is seeded
        if db.query(QuestionnaireQuestion).count() == 0:
            QuestionnaireEngine.seed_question_bank(db)

        # Check for active in-progress session
        active_session = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.patient_id == patient_id,
            QuestionnaireSession.status == SessionStatus.IN_PROGRESS
        ).order_by(QuestionnaireSession.created_at.desc()).first()

        if not active_session:
            first_q_code = QuestionnaireEngine.get_first_question_code()
            active_session = QuestionnaireSession(
                patient_id=patient_id,
                status=SessionStatus.IN_PROGRESS,
                current_question_code=first_q_code
            )
            db.add(active_session)
            db.commit()
            db.refresh(active_session)

        return cls._build_session_response(db, active_session)

    @classmethod
    def get_patient_session(
        cls,
        db: Session,
        patient_id: str,
        session_id: str
    ) -> SessionResponse:
        """Fetch an existing questionnaire session with strict patient ownership validation."""
        session = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.id == session_id,
            QuestionnaireSession.patient_id == patient_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Questionnaire session not found."
            )

        return cls._build_session_response(db, session)

    @classmethod
    def get_active_session(
        cls,
        db: Session,
        patient_id: str
    ) -> Optional[SessionResponse]:
        """Check if patient has an ongoing in-progress questionnaire session."""
        session = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.patient_id == patient_id,
            QuestionnaireSession.status == SessionStatus.IN_PROGRESS
        ).order_by(QuestionnaireSession.created_at.desc()).first()

        if not session:
            return None
        return cls._build_session_response(db, session)

    @classmethod
    def submit_answer(
        cls,
        db: Session,
        patient_id: str,
        session_id: str,
        data: AnswerSubmitRequest
    ) -> SessionResponse:
        """
        Validate and store the patient's answer, compute the deterministic next question,
        and update the session state in a single transaction.
        """
        session = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.id == session_id,
            QuestionnaireSession.patient_id == patient_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Questionnaire session not found."
            )

        if session.status != SessionStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot submit answer to a session with status '{session.status.value}'."
            )

        # Flow security check: Patient must answer the current server-selected question
        if session.current_question_code != data.question_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question order mismatch: Expected answer for '{session.current_question_code}', received '{data.question_code}'."
            )

        question = db.query(QuestionnaireQuestion).filter(
            QuestionnaireQuestion.question_code == data.question_code,
            QuestionnaireQuestion.active == True
        ).first()

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question '{data.question_code}' not found."
            )

        # Validate answer semantics
        cleaned_answer = QuestionnaireEngine.validate_answer(question, data.answer)

        try:
            # Check if answer record already exists for this (session, question)
            existing_answer = db.query(QuestionnaireAnswer).filter(
                QuestionnaireAnswer.session_id == session.id,
                QuestionnaireAnswer.question_id == question.id
            ).first()

            if existing_answer:
                existing_answer.answer = cleaned_answer
                existing_answer.answered_at = datetime.now(timezone.utc)
            else:
                new_answer = QuestionnaireAnswer(
                    session_id=session.id,
                    question_id=question.id,
                    question_code=question.question_code,
                    answer=cleaned_answer
                )
                db.add(new_answer)

            # Compute next question via deterministic branching
            next_q_code = QuestionnaireEngine.determine_next_question_code(question, cleaned_answer)

            if next_q_code is None:
                # Terminal question reached -> complete session
                session.status = SessionStatus.COMPLETED
                session.completed_at = datetime.now(timezone.utc)
                session.current_question_code = None
            else:
                session.current_question_code = next_q_code

            db.commit()
            db.refresh(session)
            return cls._build_session_response(db, session)

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process answer: {str(e)}"
            )

    @classmethod
    def complete_session(
        cls,
        db: Session,
        patient_id: str,
        session_id: str
    ) -> SessionResponse:
        """Manually mark an active session as completed."""
        session = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.id == session_id,
            QuestionnaireSession.patient_id == patient_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Questionnaire session not found."
            )

        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
        session.current_question_code = None
        db.commit()
        db.refresh(session)
        return cls._build_session_response(db, session)

    @classmethod
    def get_session_summary(
        cls,
        db: Session,
        patient_id: str,
        session_id: str
    ) -> SessionSummaryResponse:
        """
        Generate non-diagnostic structured assessment summary of the completed questionnaire.
        NO diagnostic assertions (e.g. BPPV, Meniere's) are emitted.
        """
        session = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.id == session_id,
            QuestionnaireSession.patient_id == patient_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Questionnaire session not found."
            )

        summary_items: List[AnswerSummaryItem] = []
        for ans in session.answers:
            summary_items.append(
                AnswerSummaryItem(
                    question_code=ans.question_code,
                    question_text=ans.question.question_text if ans.question else ans.question_code,
                    category=ans.question.category if ans.question else "general",
                    question_type=ans.question.question_type if ans.question else "TEXT",
                    answer=ans.answer,
                    answered_at=ans.answered_at
                )
            )

        return SessionSummaryResponse(
            session_id=session.id,
            patient_id=session.patient_id,
            status=session.status,
            started_at=session.started_at,
            completed_at=session.completed_at,
            total_questions_answered=len(summary_items),
            answers=summary_items
        )

    @staticmethod
    def _build_session_response(
        db: Session,
        session: QuestionnaireSession
    ) -> SessionResponse:
        """Map session entity to SessionResponse schema."""
        current_question_dto = None
        if session.current_question_code and session.status == SessionStatus.IN_PROGRESS:
            q = db.query(QuestionnaireQuestion).filter(
                QuestionnaireQuestion.question_code == session.current_question_code,
                QuestionnaireQuestion.active == True
            ).first()
            if q:
                current_question_dto = QuestionResponse(
                    id=q.id,
                    question_code=q.question_code,
                    version=q.version,
                    category=q.category,
                    question_type=q.question_type,
                    question_text=q.question_text,
                    options=[
                        QuestionOption(value=opt["value"], label=opt["label"])
                        for opt in (q.options or [])
                    ],
                    display_order=q.display_order
                )

        answered_count = len(session.answers)
        # Adaptive branching depth estimation is typically 6-8 questions
        estimated_total = max(answered_count + 1, 6) if session.status == SessionStatus.IN_PROGRESS else answered_count

        return SessionResponse(
            session_id=session.id,
            status=session.status,
            started_at=session.started_at,
            completed_at=session.completed_at,
            current_question=current_question_dto,
            progress=SessionProgress(
                answered_count=answered_count,
                estimated_total=estimated_total,
                current_step=answered_count + 1
            ),
            message="Questionnaire completed." if session.status == SessionStatus.COMPLETED else None
        )

