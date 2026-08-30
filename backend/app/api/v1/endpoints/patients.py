from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_patient, get_current_user
from app.models.profile import PatientProfile
from app.models.user import User
from app.schemas.profile import PatientProfileResponse, PatientProfileUpdate
from app.schemas.monitoring import DailyHealthCheckCreate, DailyHealthCheckResponse, SymptomTrendsResponse
from app.schemas.common import StandardResponse
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patient Monitoring"])


@router.get("/profile", response_model=StandardResponse[PatientProfileResponse])
def get_patient_profile(
    patient: PatientProfile = Depends(get_current_patient),
    current_user: User = Depends(get_current_user)
):
    """Fetch profile data for the currently authenticated patient."""
    resp = PatientProfileResponse(
        id=patient.id,
        user_id=patient.user_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        phone_number=patient.phone_number,
        emergency_contact_name=patient.emergency_contact_name,
        emergency_contact_phone=patient.emergency_contact_phone,
        primary_vertigo_diagnosis=patient.primary_vertigo_diagnosis,
        created_at=patient.created_at,
        updated_at=patient.updated_at
    )
    return StandardResponse(data=resp)


@router.put("/profile", response_model=StandardResponse[PatientProfileResponse])
def update_patient_profile(
    data: PatientProfileUpdate,
    patient: PatientProfile = Depends(get_current_patient),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update patient contact details and clinical baseline info."""
    if data.phone_number is not None:
        patient.phone_number = data.phone_number
    if data.emergency_contact_name is not None:
        patient.emergency_contact_name = data.emergency_contact_name
    if data.emergency_contact_phone is not None:
        patient.emergency_contact_phone = data.emergency_contact_phone
    if data.primary_vertigo_diagnosis is not None:
        patient.primary_vertigo_diagnosis = data.primary_vertigo_diagnosis

    db.commit()
    db.refresh(patient)

    resp = PatientProfileResponse(
        id=patient.id,
        user_id=patient.user_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        phone_number=patient.phone_number,
        emergency_contact_name=patient.emergency_contact_name,
        emergency_contact_phone=patient.emergency_contact_phone,
        primary_vertigo_diagnosis=patient.primary_vertigo_diagnosis,
        created_at=patient.created_at,
        updated_at=patient.updated_at
    )
    return StandardResponse(message="Patient profile updated successfully", data=resp)


@router.post("/check-ins", response_model=StandardResponse[DailyHealthCheckResponse], status_code=status.HTTP_201_CREATED)
def submit_daily_check_in(
    data: DailyHealthCheckCreate,
    patient: PatientProfile = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Submit or update daily symptom ratings, lifestyle parameters, and medication log."""
    check_in = PatientService.record_daily_check_in(db, patient.id, data)
    dto = DailyHealthCheckResponse.model_validate(check_in)
    return StandardResponse(
        message="Daily health check-in recorded successfully",
        data=dto
    )


@router.get("/check-ins", response_model=StandardResponse[List[DailyHealthCheckResponse]])
def get_daily_check_in_history(
    limit: int = 30,
    patient: PatientProfile = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Fetch historical daily symptom logs for the authenticated patient."""
    history = PatientService.get_patient_check_ins(db, patient.id, limit=limit)
    dtos = [DailyHealthCheckResponse.model_validate(h) for h in history]
    return StandardResponse(data=dtos)


@router.get("/symptom-trends", response_model=StandardResponse[SymptomTrendsResponse])
def get_symptom_trends(
    patient: PatientProfile = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Calculate rolling 7-day symptom averages and medication adherence metrics."""
    trends = PatientService.get_symptom_trends(db, patient.id)
    return StandardResponse(data=trends)
