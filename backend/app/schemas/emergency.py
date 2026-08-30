from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.emergency import EmergencySeverity, EmergencyStatus


class EmergencyEventCreateRequest(BaseModel):
    risk_assessment_id: Optional[str] = None
    severity: EmergencySeverity = EmergencySeverity.HIGH
    notes: Optional[str] = Field(None, max_length=1000)
    initiate_doctor_contact: bool = False
    initiate_emergency_contact: bool = False


class EmergencyPatientActionRequest(BaseModel):
    action: str = Field(..., pattern="^(CONTACT_DOCTOR|CONTACT_EMERGENCY_CONTACT|CANCEL)$")
    notes: Optional[str] = Field(None, max_length=1000)


class EmergencyDoctorActionRequest(BaseModel):
    action: str = Field(..., pattern="^(ACKNOWLEDGE|RESOLVE)$")
    notes: Optional[str] = Field(None, max_length=1000)


class EmergencyEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    patient_name: Optional[str] = None
    patient_dob: Optional[str] = None
    patient_gender: Optional[str] = None
    risk_assessment_id: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    severity: EmergencySeverity
    status: EmergencyStatus
    contacted_doctor: bool
    contacted_emergency_contact: bool
    contacted_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    assigned_doctor_name: Optional[str] = None
    assigned_doctor_specialization: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    notice: str = (
        "Emergency support and escalation workflow. This is NOT an automatic diagnosis or emergency dispatch service. "
        "For acute severe symptoms, please contact local emergency medical services immediately."
    )


class EmergencyEventListResponse(BaseModel):
    items: List[EmergencyEventResponse]
    total: int
    limit: int = 20
    offset: int = 0


class EmergencyContextResponse(BaseModel):
    has_emergency_contact: bool
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    has_assigned_doctor: bool
    assigned_doctor_name: Optional[str] = None
    assigned_doctor_specialization: Optional[str] = None
    latest_risk_level: Optional[str] = None
    latest_risk_score: Optional[float] = None
    latest_risk_assessment_id: Optional[str] = None
    active_event: Optional[EmergencyEventResponse] = None


class EmergencyGuidanceItem(BaseModel):
    title: str
    description: str
    category: str


class EmergencyGuidanceResponse(BaseModel):
    guidance: List[EmergencyGuidanceItem]
    disclaimer: str
