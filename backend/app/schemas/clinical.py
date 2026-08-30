from datetime import datetime, date
from typing import Optional, List, Dict, Any
from app.models.clinical import NoteType
from app.models.risk import RiskCategory
from app.schemas.common import BaseSchema
from app.schemas.monitoring import DailyHealthCheckResponse
from app.schemas.risk import RiskAssessmentResponse
from app.schemas.eye_analysis import EyeMovementFeatureResponse


class DoctorNoteCreate(BaseSchema):
    patient_id: str
    risk_assessment_id: Optional[str] = None
    note_type: NoteType = NoteType.ROUTINE_REVIEW
    content: str
    is_shared_with_patient: bool = True


class DoctorNoteResponse(BaseSchema):
    id: str
    patient_id: str
    doctor_id: str
    doctor_name: Optional[str] = None
    doctor_specialty: Optional[str] = None
    risk_assessment_id: Optional[str] = None
    note_type: NoteType
    content: str
    is_shared_with_patient: bool
    created_at: datetime
    updated_at: datetime


class PatientTriageCard(BaseSchema):
    patient_id: str
    user_id: str
    full_name: str
    date_of_birth: date
    gender: str
    phone_number: Optional[str] = None
    primary_diagnosis: Optional[str] = None
    latest_risk_score: Optional[float] = None
    latest_risk_category: Optional[RiskCategory] = None
    latest_check_in_date: Optional[date] = None
    active_emergency_alerts_count: int = 0
    assigned_status: str


class PatientDossierResponse(BaseSchema):
    patient_id: str
    user_id: str
    first_name: str
    last_name: str
    email: str
    date_of_birth: date
    gender: str
    phone_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    primary_vertigo_diagnosis: Optional[str] = None
    latest_risk: Optional[RiskAssessmentResponse] = None
    recent_check_ins: List[DailyHealthCheckResponse] = []
    recent_notes: List[DoctorNoteResponse] = []
    latest_eye_features: Optional[EyeMovementFeatureResponse] = None


class TimeSeriesPoint(BaseSchema):
    date: str
    dizziness: Optional[int] = None
    nausea: Optional[int] = None
    unsteadiness: Optional[int] = None
    risk_score: Optional[float] = None


class PatientTrendsResponse(BaseSchema):
    patient_id: str
    timeline: List[TimeSeriesPoint]
