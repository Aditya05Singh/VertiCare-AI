from datetime import date, datetime
from typing import Optional, List
from app.models.profile import Gender, AssignmentStatus
from app.schemas.common import BaseSchema


class PatientProfileBase(BaseSchema):
    date_of_birth: date
    gender: Gender = Gender.PREFER_NOT_TO_SAY
    phone_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    primary_vertigo_diagnosis: Optional[str] = "Under Initial Evaluation"


class PatientProfileCreate(PatientProfileBase):
    pass


class PatientProfileUpdate(BaseSchema):
    phone_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    primary_vertigo_diagnosis: Optional[str] = None


class PatientProfileResponse(PatientProfileBase):
    id: str
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DoctorProfileBase(BaseSchema):
    license_number: str
    specialty: str = "Otolaryngology / Neurotology"
    hospital_affiliation: Optional[str] = None


class DoctorProfileCreate(DoctorProfileBase):
    pass


class DoctorProfileUpdate(BaseSchema):
    specialty: Optional[str] = None
    hospital_affiliation: Optional[str] = None


class DoctorProfileResponse(DoctorProfileBase):
    id: str
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DoctorPatientAssignment(BaseSchema):
    doctor_id: str
    patient_id: str
    assignment_status: AssignmentStatus = AssignmentStatus.ACTIVE
