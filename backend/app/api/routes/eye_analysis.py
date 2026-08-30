from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_patient
from app.models.user import User
from app.schemas.eye_analysis import (
    EyeMovementFeaturesSubmitRequest,
    EyeAnalysisSessionResponse
)
from app.services.eye_analysis_service import EyeAnalysisService

router = APIRouter(prefix="/eye-analysis", tags=["Computer Vision Eye Movement Screening"])


def _get_patient_id(current_user: User) -> str:
    if not current_user.patient_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have an active patient profile."
        )
    return current_user.patient_profile.id


@router.post(
    "/sessions",
    response_model=EyeAnalysisSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create eye-movement analysis session"
)
def create_eye_analysis_session(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Initializes a new computer-vision screening session for the authenticated patient."""
    patient_id = _get_patient_id(current_user)
    return EyeAnalysisService.create_session(db, patient_id)


@router.post(
    "/sessions/{session_id}/features",
    response_model=EyeAnalysisSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Save extracted numerical CV eye movement features"
)
def save_eye_movement_features(
    session_id: str,
    data: EyeMovementFeaturesSubmitRequest,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Persists validated numerical CV features (amplitudes, velocities, blinks, quality scores)."""
    patient_id = _get_patient_id(current_user)
    return EyeAnalysisService.save_features(db, patient_id, session_id, data)


@router.get(
    "/sessions/{session_id}",
    response_model=EyeAnalysisSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get eye-movement session details and features"
)
def get_eye_analysis_session(
    session_id: str,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Fetch an eye analysis session by ID with strict patient ownership check."""
    patient_id = _get_patient_id(current_user)
    return EyeAnalysisService.get_session(db, patient_id, session_id)

