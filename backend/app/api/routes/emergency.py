from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User, UserRole
from app.api.deps import get_current_user, require_patient, require_doctor
from app.schemas.emergency import (
    EmergencyEventCreateRequest,
    EmergencyPatientActionRequest,
    EmergencyDoctorActionRequest,
    EmergencyEventResponse,
    EmergencyEventListResponse,
    EmergencyContextResponse,
    EmergencyGuidanceResponse,
)
from app.services.emergency_service import EmergencyService

router = APIRouter(prefix="/emergency-events", tags=["Emergency Support"])


@router.get(
    "/guidance",
    response_model=EmergencyGuidanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get static emergency safety guidance"
)
def get_emergency_guidance() -> EmergencyGuidanceResponse:
    """Returns static, non-diagnostic safety guidelines for vertigo and dizziness."""
    return EmergencyService.get_static_guidance()


@router.get(
    "/context",
    response_model=EmergencyContextResponse,
    status_code=status.HTTP_200_OK,
    summary="Get patient emergency metadata context"
)
def get_patient_emergency_context(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
) -> EmergencyContextResponse:
    """Returns emergency contacts, assigned doctor details, and latest screening risk status for the current patient."""
    return EmergencyService.get_patient_emergency_context(db, current_user.patient_profile.id)


@router.post(
    "",
    response_model=EmergencyEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an emergency support event"
)
def create_emergency_event(
    data: EmergencyEventCreateRequest,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
) -> EmergencyEventResponse:
    """
    Creates an emergency support event for the authenticated patient.
    Supports debouncing and immediate contact initiation.
    """
    return EmergencyService.create_emergency_event(db, current_user.patient_profile.id, data)


@router.get(
    "",
    response_model=EmergencyEventListResponse,
    status_code=status.HTTP_200_OK,
    summary="List emergency support events"
)
def list_emergency_events(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="Optional status filter for clinicians"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> EmergencyEventListResponse:
    """
    Lists emergency events.
    - Patients receive their own emergency events.
    - Clinicians receive emergency events belonging strictly to assigned patients.
    """
    if current_user.role == UserRole.PATIENT:
        if not current_user.patient_profile:
            raise HTTPException(status_code=403, detail="Patient profile missing.")
        return EmergencyService.get_patient_emergency_events(
            db, current_user.patient_profile.id, limit, offset
        )
    elif current_user.role == UserRole.DOCTOR:
        if not current_user.doctor_profile:
            raise HTTPException(status_code=403, detail="Doctor profile missing.")
        return EmergencyService.get_doctor_emergency_events(
            db, current_user.doctor_profile.id, limit, offset, status
        )
    else:
        raise HTTPException(status_code=403, detail="Unauthorized role.")


@router.get(
    "/{event_id}",
    response_model=EmergencyEventResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single emergency event detail"
)
def get_emergency_event_detail(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> EmergencyEventResponse:
    """Retrieves detail for a single emergency event with ownership and assignment protection."""
    return EmergencyService.get_emergency_event_by_id(db, current_user, event_id)


@router.post(
    "/{event_id}/patient-action",
    response_model=EmergencyEventResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute patient action on emergency event"
)
def execute_patient_action(
    event_id: str,
    data: EmergencyPatientActionRequest,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
) -> EmergencyEventResponse:
    """Executes a patient action (CONTACT_DOCTOR, CONTACT_EMERGENCY_CONTACT, CANCEL)."""
    return EmergencyService.patient_take_action(
        db, current_user.patient_profile.id, event_id, data.action, data.notes
    )


@router.post(
    "/{event_id}/doctor-action",
    response_model=EmergencyEventResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute doctor action on emergency event"
)
def execute_doctor_action(
    event_id: str,
    data: EmergencyDoctorActionRequest,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
) -> EmergencyEventResponse:
    """Executes a clinician status transition (ACKNOWLEDGE, RESOLVE) on an assigned patient's event."""
    return EmergencyService.doctor_take_action(
        db, current_user.doctor_profile.id, event_id, data.action, data.notes
    )

