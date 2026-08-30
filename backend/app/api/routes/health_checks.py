from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_patient
from app.models.user import User
from app.schemas.monitoring import (
    DailyHealthCheckCreate,
    DailyHealthCheckResponse,
    DailyHealthCheckListResponse,
    DailyHealthTrendResponse
)
from app.services.health_check_service import HealthCheckService

router = APIRouter(prefix="/health-checks", tags=["Daily Health Monitoring"])


def _get_patient_id(current_user: User) -> str:
    if not current_user.patient_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have an active patient profile."
        )
    return current_user.patient_profile.id


@router.post(
    "",
    response_model=DailyHealthCheckResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record daily health check"
)
def create_daily_health_check(
    data: DailyHealthCheckCreate,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """
    Record a daily health check for the authenticated patient.
    Idempotent for same calendar day (updates existing daily log).
    """
    patient_id = _get_patient_id(current_user)
    record = HealthCheckService.create_or_update_health_check(db, patient_id, data)
    return record


@router.get(
    "/trends",
    response_model=DailyHealthTrendResponse,
    status_code=status.HTTP_200_OK,
    summary="Get longitudinal health and symptom trends"
)
def get_health_trends(
    days: int = Query(30, ge=1, le=90, description="Timeframe in days (e.g. 7 or 30)"),
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Return aggregated symptom severity and lifestyle averages over the requested days range."""
    patient_id = _get_patient_id(current_user)
    return HealthCheckService.get_patient_trends(db, patient_id, days=days)


@router.get(
    "",
    response_model=DailyHealthCheckListResponse,
    status_code=status.HTTP_200_OK,
    summary="List patient health check history"
)
def list_health_checks(
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Return chronological history of daily health checks for the authenticated patient, newest first."""
    patient_id = _get_patient_id(current_user)
    items, total = HealthCheckService.get_patient_history(db, patient_id, limit=limit, offset=offset)
    return DailyHealthCheckListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get(
    "/{id}",
    response_model=DailyHealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Get specific health check details"
)
def get_health_check(
    id: str,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Fetch single health check record by ID with strict ownership validation."""
    patient_id = _get_patient_id(current_user)
    return HealthCheckService.get_patient_health_check_by_id(db, patient_id, health_check_id=id)

