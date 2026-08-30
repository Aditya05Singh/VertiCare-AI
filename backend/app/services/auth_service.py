from datetime import date
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.profile import PatientProfile, DoctorProfile, Gender
from app.schemas.auth import (
    PatientRegisterRequest,
    DoctorRegisterRequest,
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)
from app.core.security import hash_password, verify_password, create_access_token


class AuthService:
    @staticmethod
    def register_patient(db: Session, data: PatientRegisterRequest) -> User:
        """Register a patient user and create their linked PatientProfile within a single transaction."""
        norm_email = data.email.lower()
        existing = db.query(User).filter(User.email == norm_email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An account with email '{norm_email}' already exists."
            )

        user = User(
            email=norm_email,
            password_hash=hash_password(data.password),
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            role=UserRole.PATIENT,
            is_active=True
        )

        try:
            db.add(user)
            db.flush()  # Generate user.id

            profile = PatientProfile(
                user_id=user.id,
                date_of_birth=data.date_of_birth,
                gender=data.gender,
                emergency_contact_name=data.emergency_contact_name.strip() if data.emergency_contact_name else None,
                emergency_contact_phone=data.emergency_contact_phone.strip() if data.emergency_contact_phone else None,
                medical_history=data.medical_history.strip() if data.medical_history else None
            )
            db.add(profile)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to complete patient registration: {str(e)}"
            )

    @staticmethod
    def register_doctor(db: Session, data: DoctorRegisterRequest) -> User:
        """Register a clinician user and create their linked DoctorProfile within a single transaction."""
        norm_email = data.email.lower()
        existing = db.query(User).filter(User.email == norm_email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An account with email '{norm_email}' already exists."
            )

        # Check duplicate license identifier
        existing_license = db.query(DoctorProfile).filter(
            DoctorProfile.license_identifier == data.license_identifier.strip()
        ).first()
        if existing_license:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A doctor profile with license identifier '{data.license_identifier}' already exists."
            )

        user = User(
            email=norm_email,
            password_hash=hash_password(data.password),
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            role=UserRole.DOCTOR,
            is_active=True
        )

        try:
            db.add(user)
            db.flush()

            profile = DoctorProfile(
                user_id=user.id,
                specialization=data.specialization.strip(),
                license_identifier=data.license_identifier.strip()
            )
            db.add(profile)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to complete doctor registration: {str(e)}"
            )

    @classmethod
    def register_user(cls, db: Session, data: RegisterRequest) -> User:
        """Unified registration dispatcher validating role and profile fields."""
        if data.role == UserRole.PATIENT:
            if not data.date_of_birth:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Date of birth is required for patient registration."
                )
            patient_data = PatientRegisterRequest(
                email=data.email,
                password=data.password,
                first_name=data.first_name,
                last_name=data.last_name,
                date_of_birth=data.date_of_birth,
                gender=data.gender or Gender.PREFER_NOT_TO_SAY,
                emergency_contact_name=data.emergency_contact_name,
                emergency_contact_phone=data.emergency_contact_phone,
                medical_history=data.medical_history
            )
            return cls.register_patient(db, patient_data)

        elif data.role == UserRole.DOCTOR:
            if not data.specialization or not data.license_identifier:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Specialization and license identifier are required for doctor registration."
                )
            doctor_data = DoctorRegisterRequest(
                email=data.email,
                password=data.password,
                first_name=data.first_name,
                last_name=data.last_name,
                specialization=data.specialization,
                license_identifier=data.license_identifier
            )
            return cls.register_doctor(db, doctor_data)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid registration role '{data.role}'."
            )

    @classmethod
    def authenticate(cls, db: Session, data: LoginRequest) -> TokenResponse:
        """Authenticate user credentials and issue signed JWT access token."""
        norm_email = data.email.lower()
        user = db.query(User).filter(User.email == norm_email).first()

        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated."
            )

        token = create_access_token(
            user_id=user.id,
            role=user.role.value,
            email=user.email
        )

        user_dto = cls.get_user_summary(user)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user_dto
        )

    @staticmethod
    def get_user_summary(user: User) -> UserResponse:
        """Map user entity to safe UserResponse schema (no password hashes)."""
        patient_id = user.patient_profile.id if user.patient_profile else None
        doctor_id = user.doctor_profile.id if user.doctor_profile else None

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            patient_profile_id=patient_id,
            doctor_profile_id=doctor_id
        )
