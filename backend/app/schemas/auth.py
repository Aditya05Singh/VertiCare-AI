from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.models.user import UserRole
from app.models.profile import Gender


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PatientRegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: Gender = Gender.PREFER_NOT_TO_SAY
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=30)
    medical_history: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return str(v).strip().lower()


class DoctorRegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    specialization: str = Field(..., min_length=2, max_length=150)
    license_identifier: str = Field(..., min_length=3, max_length=100)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return str(v).strip().lower()


class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.PATIENT

    # Patient fields
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = Gender.PREFER_NOT_TO_SAY
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None

    # Doctor fields
    specialization: Optional[str] = None
    license_identifier: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return str(v).strip().lower()


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return str(v).strip().lower()


class UserResponse(BaseSchema):
    id: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    patient_profile_id: Optional[str] = None
    doctor_profile_id: Optional[str] = None


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
