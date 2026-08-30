from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.clinical import NoteType
from app.models.risk import RiskLevel
from app.schemas.monitoring import DailyHealthCheckResponse, DailyHealthTrendResponse
from app.schemas.risk import RiskAssessmentResponse
from app.schemas.questionnaire import SessionSummaryResponse
from app.schemas.eye_analysis import EyeAnalysisSessionResponse


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DoctorRecentActivityItem(BaseSchema):
    patient_id: str
    patient_name: str
    activity_type: str  # "HEALTH_CHECK", "QUESTIONNAIRE", "EYE_ANALYSIS", "RISK_ASSESSMENT"
    timestamp: datetime
    description: str
    risk_level: Optional[str] = None


class DoctorDashboardSummaryResponse(BaseSchema):
    total_assigned_patients: int
    risk_distribution: Dict[str, int]
    recent_activity: List[DoctorRecentActivityItem] = []


class AssignedPatientCardResponse(BaseSchema):
    patient_id: str
    full_name: str
    email: str
    date_of_birth: date
    gender: str
    assigned_at: datetime
    latest_risk_level: Optional[str] = None
    latest_risk_score: Optional[float] = None
    latest_assessment_date: Optional[datetime] = None
    latest_health_check_date: Optional[date] = None
    latest_health_check_dizziness: Optional[int] = None
    total_health_checks: int = 0


class DoctorPatientListResponse(BaseSchema):
    items: List[AssignedPatientCardResponse]
    total: int


class DoctorPatientDossierResponse(BaseSchema):
    patient_id: str
    full_name: str
    email: str
    date_of_birth: date
    gender: str
    medical_history: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    latest_health_check: Optional[DailyHealthCheckResponse] = None
    latest_questionnaire: Optional[SessionSummaryResponse] = None
    latest_eye_analysis: Optional[EyeAnalysisSessionResponse] = None
    latest_risk_assessment: Optional[RiskAssessmentResponse] = None
    recent_notes_count: int = 0


class DoctorNoteCreateRequest(BaseSchema):
    content: str = Field(..., min_length=3, max_length=5000)
    note_type: NoteType = NoteType.ROUTINE_REVIEW
    risk_assessment_id: Optional[str] = None
    is_shared_with_patient: bool = True


class DoctorNoteUpdateRequest(BaseSchema):
    content: str = Field(..., min_length=3, max_length=5000)
    note_type: Optional[NoteType] = None
    is_shared_with_patient: Optional[bool] = None


class DoctorNoteResponse(BaseSchema):
    id: str
    patient_id: str
    doctor_id: str
    doctor_name: str
    doctor_specialization: str
    risk_assessment_id: Optional[str] = None
    note_type: NoteType
    content: str
    is_shared_with_patient: bool
    created_at: datetime
    updated_at: datetime


class DoctorPatientReportResponse(BaseSchema):
    patient_id: str
    patient_name: str
    generated_at: datetime
    health_summary: Dict[str, Any]
    questionnaire_summary: Optional[Dict[str, Any]] = None
    eye_analysis_summary: Optional[Dict[str, Any]] = None
    latest_risk: Optional[RiskAssessmentResponse] = None
    clinical_notes: List[DoctorNoteResponse] = []
    disclaimer: str = "AI-assisted screening and decision support information — not a medical diagnosis."

