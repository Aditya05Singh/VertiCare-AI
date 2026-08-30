from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_patient
from app.models.user import User
from app.schemas.risk import (
    RiskAssessmentCreateRequest,
    RiskAssessmentResponse,
    RiskAssessmentListResponse
)
from app.services.risk_assessment_service import RiskAssessmentService

router = APIRouter(prefix="/risk-assessment", tags=["AI Risk Engine & Multimodal Assessment"])


def _get_patient_id(current_user: User) -> str:
    if not current_user.patient_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have an active patient profile."
        )
    return current_user.patient_profile.id


@router.post(
    "",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute AI-assisted screening risk assessment"
)
def compute_risk_assessment(
    data: Optional[RiskAssessmentCreateRequest] = None,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """
    Evaluates patient's multimodal inputs (daily monitoring, questionnaire, and eye kinematics),
    executes calibrated ML risk inference, and returns a controlled LOW/MEDIUM/HIGH screening estimate.
    """
    patient_id = _get_patient_id(current_user)
    request_data = data or RiskAssessmentCreateRequest()
    return RiskAssessmentService.evaluate_patient_risk(db, patient_id, request_data)


@router.get(
    "/history",
    response_model=RiskAssessmentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get patient risk assessment history"
)
def get_risk_assessment_history(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Retrieves chronological risk assessment history for the authenticated patient."""
    patient_id = _get_patient_id(current_user)
    return RiskAssessmentService.get_history(db, patient_id, limit, offset)


@router.get(
    "/{id}",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get risk assessment by ID"
)
def get_risk_assessment_by_id(
    id: str,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Fetches a specific risk assessment by ID with strict ownership validation."""
    patient_id = _get_patient_id(current_user)
    return RiskAssessmentService.get_assessment(db, patient_id, id)

