from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_doctor, require_doctor_patient_access
from app.models.user import User
from app.models.profile import PatientProfile
from app.schemas.doctor import (
    DoctorDashboardSummaryResponse,
    DoctorPatientListResponse,
    DoctorPatientDossierResponse,
    DoctorNoteCreateRequest,
    DoctorNoteUpdateRequest,
    DoctorNoteResponse,
    DoctorPatientReportResponse
)
from app.schemas.monitoring import (
    DailyHealthCheckListResponse,
    DailyHealthTrendResponse
)
from app.schemas.questionnaire import SessionSummaryResponse
from app.schemas.eye_analysis import EyeAnalysisSessionResponse
from app.schemas.risk import RiskAssessmentListResponse
from app.services.doctor_service import DoctorService

router = APIRouter(prefix="/doctor", tags=["Clinician Portal & Patient Monitoring"])


@router.get(
    "/dashboard",
    response_model=DoctorDashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get doctor dashboard overview and assigned patient summary"
)
@router.get(
    "/dashboard/summary",
    response_model=DoctorDashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
def get_doctor_dashboard(
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Retrieves real summary metrics and recent activity for patients assigned to current doctor."""
    return DoctorService.get_dashboard_summary(db, current_user.doctor_profile.id)


@router.get(
    "/patients",
    response_model=DoctorPatientListResponse,
    status_code=status.HTTP_200_OK,
    summary="List assigned patients with search and risk filters"
)
def get_assigned_patients(
    search: Optional[str] = Query(None, description="Search by patient full name or email"),
    risk_filter: Optional[str] = Query(None, description="Filter by risk tier: HIGH, MEDIUM, LOW, UNASSESSED"),
    sort_by: str = Query("recent", description="Sort order: recent, risk_high_to_low, name"),
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Retrieves assigned patients list with search, risk categorization filtering, and sorting."""
    return DoctorService.get_assigned_patients(
        db=db,
        doctor_id=current_user.doctor_profile.id,
        search=search,
        risk_filter=risk_filter,
        sort_by=sort_by
    )


@router.get(
    "/patients/{patient_id}",
    response_model=DoctorPatientDossierResponse,
    status_code=status.HTTP_200_OK,
    summary="Get comprehensive patient clinical overview"
)
def get_patient_dossier(
    patient_id: str,
    patient: PatientProfile = Depends(require_doctor_patient_access),
    db: Session = Depends(get_db)
):
    """Retrieves patient summary profile and latest monitoring status across modalities."""
    return DoctorService.get_patient_dossier(db, patient)


@router.get(
    "/patients/{patient_id}/health",
    response_model=DailyHealthCheckListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get assigned patient daily health check log"
)
def get_patient_health_history(
    patient_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    patient: PatientProfile = Depends(require_doctor_patient_access),
    db: Session = Depends(get_db)
):
    """Retrieves chronological daily health check entries for the authorized patient."""
    return DoctorService.get_patient_health_history(db, patient.id, limit, offset)


@router.get(
    "/patients/{patient_id}/health/trends",
    response_model=DailyHealthTrendResponse,
    status_code=status.HTTP_200_OK,
    summary="Get assigned patient longitudinal health trends"
)
def get_patient_health_trends(
    patient_id: str,
    days: int = Query(14, ge=3, le=90),
    patient: PatientProfile = Depends(require_doctor_patient_access),
    db: Session = Depends(get_db)
):
    """Calculates multi-day symptom severity, sleep, stress, and trigger trends."""
    return DoctorService.get_patient_health_trends(db, patient.id, days)


@router.get(
    "/patients/{patient_id}/questionnaire",
    response_model=List[SessionSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get assigned patient completed questionnaires"
)
def get_patient_questionnaires(
    patient_id: str,
    patient: PatientProfile = Depends(require_doctor_patient_access),
    db: Session = Depends(get_db)
):
    """Retrieves completed questionnaire screening sessions and structured patient responses."""
    return DoctorService.get_patient_questionnaire_history(db, patient.id)


@router.get(
    "/patients/{patient_id}/eye-analysis",
    response_model=List[EyeAnalysisSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get assigned patient eye-movement screening history"
)
def get_patient_eye_analyses(
    patient_id: str,
    patient: PatientProfile = Depends(require_doctor_patient_access),
    db: Session = Depends(get_db)
):
    """Retrieves eye-movement screening sessions, tracking quality metrics, and kinematic features."""
    return DoctorService.get_patient_eye_analysis_history(db, patient.id)


@router.get(
    "/patients/{patient_id}/risk",
    response_model=RiskAssessmentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get assigned patient AI risk assessment history"
)
def get_patient_risk_history(
    patient_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    patient: PatientProfile = Depends(require_doctor_patient_access),
    db: Session = Depends(get_db)
):
    """Retrieves AI-assisted screening risk assessment history with model versioning and factors."""
    return DoctorService.get_patient_risk_history(db, patient.id, limit, offset)


@router.get(
    "/patients/{patient_id}/notes",
    response_model=List[DoctorNoteResponse],
    status_code=status.HTTP_200_OK,
    summary="Get clinical notes for an assigned patient"
)
def get_patient_clinical_notes(
    patient_id: str,
    patient: PatientProfile = Depends(require_doctor_patient_access),
    db: Session = Depends(get_db)
):
    """Retrieves all clinical decision support notes authored for this patient."""
    return DoctorService.get_patient_notes(db, patient.id)


@router.post(
    "/patients/{patient_id}/notes",
    response_model=DoctorNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new clinical note for an assigned patient"
)
def create_patient_clinical_note(
    patient_id: str,
    data: DoctorNoteCreateRequest,
    patient: PatientProfile = Depends(require_doctor_patient_access),
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Authors a new clinical note attached to the assigned patient."""
    return DoctorService.create_patient_note(db, current_user.doctor_profile, patient.id, data)


@router.patch(
    "/notes/{note_id}",
    response_model=DoctorNoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a clinical note authored by current doctor"
)
def update_clinical_note(
    note_id: str,
    data: DoctorNoteUpdateRequest,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Updates an existing clinical note. Clinicians may only edit notes authored by themselves."""
    return DoctorService.update_doctor_note(db, current_user.doctor_profile.id, note_id, data)


@router.get(
    "/patients/{patient_id}/reports",
    response_model=DoctorPatientReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get consolidated clinical report summary"
)
def get_patient_report_summary(
    patient_id: str,
    patient: PatientProfile = Depends(require_doctor_patient_access),
    db: Session = Depends(get_db)
):
    """Compiles multi-modal health trends, questionnaire answers, eye kinematics, and clinical notes."""
    return DoctorService.get_patient_report_summary(db, patient)

