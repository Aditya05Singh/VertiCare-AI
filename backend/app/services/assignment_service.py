from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.profile import PatientProfile, DoctorProfile, DoctorPatient
from app.schemas.assignment import (
    AssignmentCreateRequest,
    DoctorPatientAssignmentResponse,
    AssignedDoctorResponse,
    AssignedDoctorPublicProfile
)


class AssignmentService:
    @staticmethod
    def create_assignment(
        db: Session,
        current_user: User,
        data: AssignmentCreateRequest
    ) -> DoctorPatientAssignmentResponse:
        """
        Creates a mutual DoctorPatient assignment relationship.
        Supports both Clinician-initiated (via Patient ID) and Patient-initiated (via Doctor ID) flows.
        """
        doctor_profile: Optional[DoctorProfile] = None
        patient_profile: Optional[PatientProfile] = None

        if current_user.role == UserRole.DOCTOR:
            doctor_profile = current_user.doctor_profile
            if not doctor_profile:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Authenticated clinician does not have an active DoctorProfile."
                )

            patient_identifier = (data.patient_id or data.doctor_id or "").strip()
            if not patient_identifier:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Patient ID is required to create an assignment."
                )

            # Resolve patient by PatientProfile.id or User.id
            patient_profile = db.query(PatientProfile).filter(
                (PatientProfile.id == patient_identifier) | (PatientProfile.user_id == patient_identifier)
            ).first()

            if not patient_profile:
                # Check if it was an invalid user ID with different role
                user_match = db.query(User).filter(User.id == patient_identifier).first()
                if user_match and user_match.role != UserRole.PATIENT:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="The provided ID belongs to a Doctor account, not a Patient."
                    )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Patient not found for ID '{patient_identifier}'."
                )

        elif current_user.role == UserRole.PATIENT:
            patient_profile = current_user.patient_profile
            if not patient_profile:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Authenticated user does not have an active PatientProfile."
                )

            doctor_identifier = (data.doctor_id or data.patient_id or "").strip()
            if not doctor_identifier:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Doctor ID is required to create an assignment."
                )

            # Resolve doctor by DoctorProfile.id or User.id
            doctor_profile = db.query(DoctorProfile).filter(
                (DoctorProfile.id == doctor_identifier) | (DoctorProfile.user_id == doctor_identifier)
            ).first()

            if not doctor_profile:
                # Check if it was an invalid user ID with different role
                user_match = db.query(User).filter(User.id == doctor_identifier).first()
                if user_match and user_match.role != UserRole.DOCTOR:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="The provided ID belongs to a Patient account, not a Doctor."
                    )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Doctor not found for ID '{doctor_identifier}'."
                )

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authenticated Clinicians or Patients can create clinical assignments."
            )

        # Verify role types
        if patient_profile.user.role != UserRole.PATIENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target account must be a registered Patient."
            )
        if doctor_profile.user.role != UserRole.DOCTOR:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target account must be a registered Doctor."
            )

        # Check for existing duplicate assignment
        existing = db.query(DoctorPatient).filter(
            DoctorPatient.doctor_id == doctor_profile.id,
            DoctorPatient.patient_id == patient_profile.id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Patient is already assigned to this doctor."
            )

        # Create single canonical relationship record
        assignment = DoctorPatient(
            doctor_id=doctor_profile.id,
            patient_id=patient_profile.id
        )

        try:
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist doctor-patient assignment."
            )

        doc_user = doctor_profile.user
        pat_user = patient_profile.user

        return DoctorPatientAssignmentResponse(
            id=assignment.id,
            doctor_id=doctor_profile.id,
            patient_id=patient_profile.id,
            doctor_user_id=doc_user.id,
            patient_user_id=pat_user.id,
            doctor_name=f"Dr. {doc_user.first_name} {doc_user.last_name}",
            doctor_specialization=doctor_profile.specialization,
            doctor_license=doctor_profile.license_identifier,
            patient_name=f"{pat_user.first_name} {pat_user.last_name}",
            patient_email=pat_user.email,
            assigned_at=assignment.assigned_at
        )

    @staticmethod
    def get_assigned_doctor(
        db: Session,
        patient_profile_id: str
    ) -> AssignedDoctorResponse:
        """Retrieves assigned clinician information for the authorized patient."""
        assignment = db.query(DoctorPatient).filter(
            DoctorPatient.patient_id == patient_profile_id
        ).first()

        if not assignment or not assignment.doctor:
            return AssignedDoctorResponse(has_assigned_doctor=False)

        doctor = assignment.doctor
        doc_user = doctor.user

        return AssignedDoctorResponse(
            has_assigned_doctor=True,
            assignment_id=assignment.id,
            doctor_id=doctor.id,
            doctor_user_id=doc_user.id,
            doctor_name=f"Dr. {doc_user.first_name} {doc_user.last_name}",
            specialization=doctor.specialization,
            license_identifier=doctor.license_identifier,
            assigned_at=assignment.assigned_at
        )

    @staticmethod
    def get_doctor_public_profile(
        db: Session,
        current_user: User,
        doctor_id: str
    ) -> AssignedDoctorPublicProfile:
        """Retrieves public clinical profile of an assigned doctor."""
        doctor = db.query(DoctorProfile).filter(
            (DoctorProfile.id == doctor_id) | (DoctorProfile.user_id == doctor_id)
        ).first()

        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found."
            )

        # If patient requests, verify assignment relation
        if current_user.role == UserRole.PATIENT:
            assignment = db.query(DoctorPatient).filter(
                DoctorPatient.doctor_id == doctor.id,
                DoctorPatient.patient_id == current_user.patient_profile.id
            ).first()
            if not assignment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="You are not currently assigned to this doctor."
                )

        doc_user = doctor.user
        return AssignedDoctorPublicProfile(
            doctor_id=doctor.id,
            doctor_user_id=doc_user.id,
            full_name=f"Dr. {doc_user.first_name} {doc_user.last_name}",
            specialization=doctor.specialization,
            license_identifier=doctor.license_identifier,
            assigned_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def delete_assignment(
        db: Session,
        current_user: User,
        assignment_id: str
    ) -> dict:
        """Removes an active doctor-patient assignment."""
        assignment = db.query(DoctorPatient).filter(
            DoctorPatient.id == assignment_id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment relationship not found."
            )

        # Verify authorization: must be the assigned doctor or assigned patient
        is_assigned_doctor = (
            current_user.role == UserRole.DOCTOR
            and current_user.doctor_profile
            and current_user.doctor_profile.id == assignment.doctor_id
        )
        is_assigned_patient = (
            current_user.role == UserRole.PATIENT
            and current_user.patient_profile
            and current_user.patient_profile.id == assignment.patient_id
        )

        if not (is_assigned_doctor or is_assigned_patient):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to remove this assignment."
            )

        try:
            db.delete(assignment)
            db.commit()
            return {"message": "Assignment relationship successfully removed."}
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove assignment."
            )
