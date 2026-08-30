from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user, require_patient, require_doctor
from app.models.user import User
from app.schemas.auth import (
    PatientRegisterRequest,
    DoctorRegisterRequest,
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Access"])


@router.post(
    "/register/patient",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Patient account"
)
def register_patient(data: PatientRegisterRequest, db: Session = Depends(get_db)):
    """Register a new patient user and create their PatientProfile in a single transaction."""
    user = AuthService.register_patient(db, data)
    return AuthService.get_user_summary(user)


@router.post(
    "/register/doctor",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Doctor account"
)
def register_doctor(data: DoctorRegisterRequest, db: Session = Depends(get_db)):
    """Register a new clinician user and create their DoctorProfile in a single transaction."""
    user = AuthService.register_doctor(db, data)
    return AuthService.get_user_summary(user)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Unified user registration endpoint"
)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    """Unified registration route accepting patient or doctor role specification."""
    user = AuthService.register_user(db, data)
    return AuthService.get_user_summary(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT access token"
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with normalized email and password to receive JWT access token."""
    return AuthService.authenticate(db, data)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile"
)
def get_current_authenticated_user(current_user: User = Depends(get_current_user)):
    """Return the profile and role details of the current authenticated user."""
    return AuthService.get_user_summary(current_user)


# Minimal protected endpoints strictly for testing role-based authorization in Step 3
@router.get(
    "/test-patient",
    status_code=status.HTTP_200_OK,
    summary="Verify Patient-only authorization"
)
def test_patient_authorization(patient_user: User = Depends(require_patient)):
    return {
        "status": "authorized",
        "role": patient_user.role.value,
        "message": f"Welcome Patient {patient_user.full_name}"
    }


@router.get(
    "/test-doctor",
    status_code=status.HTTP_200_OK,
    summary="Verify Doctor-only authorization"
)
def test_doctor_authorization(doctor_user: User = Depends(require_doctor)):
    return {
        "status": "authorized",
        "role": doctor_user.role.value,
        "message": f"Welcome Doctor {doctor_user.full_name}"
    }

