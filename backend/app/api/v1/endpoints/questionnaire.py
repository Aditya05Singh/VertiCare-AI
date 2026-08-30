from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_patient
from app.models.profile import PatientProfile
from app.schemas.questionnaire import (
    AnswerSubmitDTO,
    NextQuestionResponse,
    QuestionnaireSessionSummary,
)
from app.schemas.common import StandardResponse
from app.services.questionnaire_engine import QuestionnaireEngine

router = APIRouter(prefix="/questionnaire", tags=["Adaptive Questionnaire"])


@router.post("/sessions/start", response_model=StandardResponse[NextQuestionResponse], status_code=status.HTTP_201_CREATED)
def start_screening_session(
    patient: PatientProfile = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Initialize a new adaptive screening session and return the first relevant question."""
    # Ensure question bank is seeded
    QuestionnaireEngine.initialize_question_bank(db)

    session = QuestionnaireEngine.start_session(db, patient.id)
    next_q = QuestionnaireEngine.get_next_question(db, session.id)
    return StandardResponse(
        message="Adaptive screening session started",
        data=next_q
    )


@router.get("/sessions/{session_id}/next", response_model=StandardResponse[NextQuestionResponse])
def get_next_question(
    session_id: str,
    patient: PatientProfile = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Retrieve the next context-dependent question for an in-progress session."""
    next_q = QuestionnaireEngine.get_next_question(db, session_id)
    return StandardResponse(data=next_q)


@router.post("/sessions/{session_id}/answer", response_model=StandardResponse[NextQuestionResponse])
def submit_answer(
    session_id: str,
    data: AnswerSubmitDTO,
    patient: PatientProfile = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Submit an answer to the current question and evaluate the dynamic branch."""
    QuestionnaireEngine.submit_answer(db, session_id, data)
    next_q = QuestionnaireEngine.get_next_question(db, session_id)
    return StandardResponse(
        message="Answer recorded",
        data=next_q
    )


@router.get("/sessions/{session_id}/summary", response_model=StandardResponse[QuestionnaireSessionSummary])
def get_session_summary(
    session_id: str,
    patient: PatientProfile = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Fetch completed session response summary and derived clinical indicators."""
    summary = QuestionnaireEngine.get_session_summary(db, session_id)
    return StandardResponse(data=summary)
