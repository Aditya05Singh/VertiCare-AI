from typing import Generator, Optional, List
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.core.security import decode_token
from app.core.exceptions import AuthException, PermissionDeniedException, ResourceNotFoundException
from app.models.user import User, UserRole
from app.models.profile import PatientProfile, DoctorProfile

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Validate bearer JWT token and return active User record."""
    payload = decode_token(token)
    if not payload:
        raise AuthException("Invalid or expired authentication token")
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise AuthException("Token payload missing subject identifier")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthException("User associated with this token does not exist")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or deactivated"
        )
    return user


def require_role(allowed_roles: List[UserRole]):
    """Enforce Role-Based Access Control (RBAC) on endpoints."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedException(
                f"Access requires one of the following roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


def get_current_patient(
    current_user: User = Depends(require_role([UserRole.PATIENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
) -> PatientProfile:
    """Resolve the PatientProfile for the authenticated patient user."""
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        raise ResourceNotFoundException("Patient profile not configured for this user account")
    return profile


def get_current_doctor(
    current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.ADMIN])),
    db: Session = Depends(get_db)
) -> DoctorProfile:
    """Resolve the DoctorProfile for the authenticated clinician user."""
    profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == current_user.id).first()
    if not profile:
        raise ResourceNotFoundException("Doctor credentials profile not found for this user account")
    return profile
