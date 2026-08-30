from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import verify_token
from app.models.user import User, UserRole
from app.models.profile import PatientProfile, DoctorProfile, DoctorPatient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=True)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Validate JWT access token and return current active User record."""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    return user


def require_patient(
    current_user: User = Depends(get_current_user)
) -> User:
    """Authorize access for users with role PATIENT."""
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: This action requires a Patient account."
        )
    return current_user


def require_doctor(
    current_user: User = Depends(get_current_user)
) -> User:
    """Authorize access for users with role DOCTOR."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: This action requires a Doctor account."
        )
    if not current_user.doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Doctor profile record is missing."
        )
    return current_user


def require_doctor_patient_access(
    patient_id: str,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
) -> PatientProfile:
    """
    Strict authorization dependency for clinician patient access.
    Verifies:
    1. Authenticated user has DOCTOR role and valid DoctorProfile.
    2. Requested PatientProfile exists (matches PatientProfile.id or User.id).
    3. Active DoctorPatient assignment exists linking doctor_id (DoctorProfile.id) and patient_id (PatientProfile.id).
    If any check fails, raises HTTP 404 (preventing IDOR and patient existence leakage).
    """
    doctor_id = current_user.doctor_profile.id

    patient = db.query(PatientProfile).filter(
        (PatientProfile.id == patient_id) | (PatientProfile.user_id == patient_id)
    ).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not assigned to current doctor."
        )

    assignment = db.query(DoctorPatient).filter(
        DoctorPatient.doctor_id == doctor_id,
        DoctorPatient.patient_id == patient.id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not assigned to current doctor."
        )

    return patient
