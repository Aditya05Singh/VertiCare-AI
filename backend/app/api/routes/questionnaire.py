from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_patient
from app.models.user import User
from app.schemas.questionnaire import (
    AnswerSubmitRequest,
    SessionResponse,
    SessionSummaryResponse
)
from app.services.questionnaire_service import QuestionnaireService

router = APIRouter(prefix="/questionnaire", tags=["Adaptive Intelligent Questionnaire"])


def _get_patient_id(current_user: User) -> str:
    if not current_user.patient_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have an active patient profile."
        )
    return current_user.patient_profile.id


@router.get(
    "/start",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Start new questionnaire session or resume active session"
)
def start_or_resume_questionnaire(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Initializes or resumes a deterministic adaptive questionnaire session for the authenticated patient."""
    patient_id = _get_patient_id(current_user)
    return QuestionnaireService.start_or_resume_session(db, patient_id)


@router.get(
    "/active",
    response_model=Optional[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Check for ongoing active in-progress session"
)
def check_active_session(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Returns active in-progress session if one exists for the patient."""
    patient_id = _get_patient_id(current_user)
    return QuestionnaireService.get_active_session(db, patient_id)


@router.get(
    "/session/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get questionnaire session by ID"
)
def get_questionnaire_session(
    session_id: str,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Resume an existing questionnaire session with strict ownership check."""
    patient_id = _get_patient_id(current_user)
    return QuestionnaireService.get_patient_session(db, patient_id, session_id)


@router.post(
    "/session/{session_id}/answer",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit answer to current question"
)
def submit_question_answer(
    session_id: str,
    data: AnswerSubmitRequest,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """
    Submits answer for current server-selected question, executes branching rule,
    and returns next question or completion status.
    """
    patient_id = _get_patient_id(current_user)
    return QuestionnaireService.submit_answer(db, patient_id, session_id, data)


@router.post(
    "/session/{session_id}/complete",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete questionnaire session"
)
def complete_questionnaire_session(
    session_id: str,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Marks the specified questionnaire session as completed."""
    patient_id = _get_patient_id(current_user)
    return QuestionnaireService.complete_session(db, patient_id, session_id)


@router.get(
    "/session/{session_id}/summary",
    response_model=SessionSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get non-diagnostic structured assessment summary"
)
def get_questionnaire_summary(
    session_id: str,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Returns safe structured responses. Does NOT emit disease diagnoses or treatment prescriptions."""
    patient_id = _get_patient_id(current_user)
    return QuestionnaireService.get_session_summary(db, patient_id, session_id)

