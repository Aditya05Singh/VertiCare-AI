from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import get_current_user, require_doctor, require_patient
from app.models.user import User
from app.schemas.assignment import (
    AssignmentCreateRequest,
    DoctorPatientAssignmentResponse,
    AssignedDoctorResponse,
    AssignedDoctorPublicProfile
)
from app.schemas.doctor import DoctorPatientListResponse
from app.services.assignment_service import AssignmentService
from app.services.doctor_service import DoctorService

router = APIRouter(tags=["Clinical Assignments"])


@router.post(
    "/assignments",
    response_model=DoctorPatientAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create mutual doctor-patient assignment"
)
def create_assignment(
    data: AssignmentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a mutual clinical assignment relationship.
    Clinicians provide Patient ID; Patients provide Doctor ID.
    Validates account existence, role types, and prevents duplicates.
    """
    return AssignmentService.create_assignment(db, current_user, data)


@router.get(
    "/patient/assigned-doctor",
    response_model=AssignedDoctorResponse,
    status_code=status.HTTP_200_OK,
    summary="Get patient's assigned doctor information"
)
def get_patient_assigned_doctor(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Retrieves assigned clinician details for the current authenticated patient."""
    return AssignmentService.get_assigned_doctor(db, current_user.patient_profile.id)


@router.get(
    "/patient/doctor-profile/{doctor_id}",
    response_model=AssignedDoctorPublicProfile,
    status_code=status.HTTP_200_OK,
    summary="View assigned doctor public profile"
)
def get_doctor_profile_for_patient(
    doctor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves professional profile details of an assigned clinician."""
    return AssignmentService.get_doctor_public_profile(db, current_user, doctor_id)


@router.get(
    "/doctor/assigned-patients",
    response_model=DoctorPatientListResponse,
    status_code=status.HTTP_200_OK,
    summary="List patients assigned to current doctor"
)
def get_doctor_assigned_patients(
    search: Optional[str] = Query(None),
    risk_filter: Optional[str] = Query(None),
    sort_by: str = Query("recent"),
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Retrieves list of patients assigned to the authenticated clinician."""
    return DoctorService.get_assigned_patients(
        db=db,
        doctor_id=current_user.doctor_profile.id,
        search=search,
        risk_filter=risk_filter,
        sort_by=sort_by
    )


@router.delete(
    "/assignments/{assignment_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove a doctor-patient assignment"
)
def remove_assignment(
    assignment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Removes an active clinical assignment. Requester must be the assigned clinician or patient."""
    return AssignmentService.delete_assignment(db, current_user, assignment_id)

