from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AssignmentCreateRequest(BaseSchema):
    doctor_id: Optional[str] = Field(None, description="Doctor Profile ID or User ID (used when patient initiates)")
    patient_id: Optional[str] = Field(None, description="Patient Profile ID or User ID (used when doctor initiates)")


class DoctorPatientAssignmentResponse(BaseSchema):
    id: str
    doctor_id: str
    patient_id: str
    doctor_user_id: str
    patient_user_id: str
    doctor_name: str
    doctor_specialization: str
    doctor_license: str
    patient_name: str
    patient_email: str
    assigned_at: datetime
    notice: str = "Active mutual clinical assignment between clinician and patient."


class AssignedDoctorResponse(BaseSchema):
    has_assigned_doctor: bool
    assignment_id: Optional[str] = None
    doctor_id: Optional[str] = None
    doctor_user_id: Optional[str] = None
    doctor_name: Optional[str] = None
    specialization: Optional[str] = None
    license_identifier: Optional[str] = None
    assigned_at: Optional[datetime] = None


class AssignedDoctorPublicProfile(BaseSchema):
    doctor_id: str
    doctor_user_id: str
    full_name: str
    specialization: str
    license_identifier: str
    assigned_at: Optional[datetime] = None
    notice: str = "Authorized clinician profile."

