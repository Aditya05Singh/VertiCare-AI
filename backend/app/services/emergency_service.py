from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.profile import PatientProfile, DoctorProfile, DoctorPatient
from app.models.risk import RiskAssessment, RiskLevel
from app.models.emergency import EmergencyEvent, EmergencySeverity, EmergencyStatus
from app.schemas.emergency import (
    EmergencyEventCreateRequest,
    EmergencyEventResponse,
    EmergencyEventListResponse,
    EmergencyContextResponse,
    EmergencyGuidanceItem,
    EmergencyGuidanceResponse,
)


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EmergencyService:
    @staticmethod
    def _format_event_response(db: Session, event: EmergencyEvent) -> EmergencyEventResponse:
        """Helper to assemble a rich EmergencyEventResponse with patient, doctor, and risk metadata."""
        patient = event.patient
        patient_user = patient.user if patient else None

        # Resolve assigned doctor
        assigned_doc_name = None
        assigned_doc_spec = None
        if patient:
            assignment = db.query(DoctorPatient).filter(DoctorPatient.patient_id == patient.id).first()
            if assignment and assignment.doctor and assignment.doctor.user:
                assigned_doc_name = f"Dr. {assignment.doctor.user.first_name} {assignment.doctor.user.last_name}"
                assigned_doc_spec = assignment.doctor.specialization

        # Resolve risk info
        risk_level = None
        risk_score = None
        if event.risk_assessment:
            risk_level = event.risk_assessment.risk_level.value if hasattr(event.risk_assessment.risk_level, 'value') else str(event.risk_assessment.risk_level)
            risk_score = event.risk_assessment.risk_score

        return EmergencyEventResponse(
            id=event.id,
            patient_id=event.patient_id,
            patient_name=f"{patient_user.first_name} {patient_user.last_name}" if patient_user else "Patient",
            patient_dob=patient.date_of_birth.isoformat() if patient and patient.date_of_birth else None,
            patient_gender=patient.gender.value if patient and hasattr(patient.gender, 'value') else str(patient.gender) if patient else None,
            risk_assessment_id=event.risk_assessment_id,
            risk_level=risk_level,
            risk_score=risk_score,
            severity=event.severity,
            status=event.status,
            contacted_doctor=event.contacted_doctor,
            contacted_emergency_contact=event.contacted_emergency_contact,
            contacted_at=event.contacted_at,
            notes=event.notes,
            created_at=event.created_at,
            updated_at=event.updated_at,
            assigned_doctor_name=assigned_doc_name,
            assigned_doctor_specialization=assigned_doc_spec,
            emergency_contact_name=patient.emergency_contact_name if patient else None,
            emergency_contact_phone=patient.emergency_contact_phone if patient else None,
        )

    @staticmethod
    def create_emergency_event(
        db: Session,
        patient_id: str,
        data: EmergencyEventCreateRequest
    ) -> EmergencyEventResponse:
        """
        Creates an emergency support event for the authenticated patient.
        Includes duplicate-click debouncing (reuses recent active event within 30s).
        """
        patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found."
            )

        # Validate risk assessment if provided
        if data.risk_assessment_id:
            risk_record = db.query(RiskAssessment).filter(
                RiskAssessment.id == data.risk_assessment_id,
                RiskAssessment.patient_id == patient_id
            ).first()
            if not risk_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Referenced risk assessment not found or does not belong to this patient."
                )

        now = get_utc_now()
        thirty_secs_ago = now - timedelta(seconds=30)

        # Debounce rapid double-clicks
        recent_active = db.query(EmergencyEvent).filter(
            EmergencyEvent.patient_id == patient_id,
            EmergencyEvent.created_at >= thirty_secs_ago,
            EmergencyEvent.status.in_([EmergencyStatus.PENDING, EmergencyStatus.CONTACT_INITIATED])
        ).first()

        if recent_active:
            if data.initiate_doctor_contact:
                recent_active.contacted_doctor = True
                recent_active.contacted_at = now
                recent_active.status = EmergencyStatus.CONTACT_INITIATED
            if data.initiate_emergency_contact:
                recent_active.contacted_emergency_contact = True
                recent_active.contacted_at = now
                recent_active.status = EmergencyStatus.CONTACT_INITIATED
            if data.notes:
                recent_active.notes = data.notes
            db.commit()
            db.refresh(recent_active)
            return EmergencyService._format_event_response(db, recent_active)

        initial_status = EmergencyStatus.PENDING
        contacted_at = None
        contacted_doc = False
        contacted_ec = False

        if data.initiate_doctor_contact or data.initiate_emergency_contact:
            initial_status = EmergencyStatus.CONTACT_INITIATED
            contacted_at = now
            contacted_doc = bool(data.initiate_doctor_contact)
            contacted_ec = bool(data.initiate_emergency_contact)

        event = EmergencyEvent(
            patient_id=patient_id,
            risk_assessment_id=data.risk_assessment_id,
            severity=data.severity,
            status=initial_status,
            contacted_doctor=contacted_doc,
            contacted_emergency_contact=contacted_ec,
            contacted_at=contacted_at,
            notes=data.notes
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        return EmergencyService._format_event_response(db, event)

    @staticmethod
    def get_patient_emergency_events(
        db: Session,
        patient_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> EmergencyEventListResponse:
        """Retrieves paginated emergency events for the authenticated patient."""
        query = db.query(EmergencyEvent).filter(EmergencyEvent.patient_id == patient_id)
        total = query.count()
        items = query.order_by(desc(EmergencyEvent.created_at)).offset(offset).limit(limit).all()

        return EmergencyEventListResponse(
            items=[EmergencyService._format_event_response(db, item) for item in items],
            total=total,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def get_doctor_emergency_events(
        db: Session,
        doctor_id: str,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> EmergencyEventListResponse:
        """
        Retrieves emergency events belonging ONLY to patients assigned to this doctor.
        Protects against unauthorized cross-patient data exposure.
        """
        assigned_patient_ids = [
            r[0] for r in db.query(DoctorPatient.patient_id).filter(DoctorPatient.doctor_id == doctor_id).all()
        ]

        if not assigned_patient_ids:
            return EmergencyEventListResponse(items=[], total=0, limit=limit, offset=offset)

        query = db.query(EmergencyEvent).filter(EmergencyEvent.patient_id.in_(assigned_patient_ids))

        if status_filter and status_filter.upper() in [e.value for e in EmergencyStatus]:
            query = query.filter(EmergencyEvent.status == EmergencyStatus(status_filter.upper()))

        total = query.count()
        items = query.order_by(desc(EmergencyEvent.created_at)).offset(offset).limit(limit).all()

        return EmergencyEventListResponse(
            items=[EmergencyService._format_event_response(db, item) for item in items],
            total=total,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def get_emergency_event_by_id(
        db: Session,
        user: User,
        event_id: str
    ) -> EmergencyEventResponse:
        """
        Retrieves a single emergency event with strict ownership or assignment check.
        Returns HTTP 404 for unassigned or missing records.
        """
        event = db.query(EmergencyEvent).filter(EmergencyEvent.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency event not found or access denied."
            )

        if user.role == UserRole.PATIENT:
            if not user.patient_profile or event.patient_id != user.patient_profile.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Emergency event not found or access denied."
                )
        elif user.role == UserRole.DOCTOR:
            if not user.doctor_profile:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Doctor profile missing."
                )
            assignment = db.query(DoctorPatient).filter(
                DoctorPatient.doctor_id == user.doctor_profile.id,
                DoctorPatient.patient_id == event.patient_id
            ).first()
            if not assignment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Emergency event not found or access denied."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized role."
            )

        return EmergencyService._format_event_response(db, event)

    @staticmethod
    def patient_take_action(
        db: Session,
        patient_id: str,
        event_id: str,
        action: str,
        notes: Optional[str] = None
    ) -> EmergencyEventResponse:
        """
        Executes a controlled patient action (CONTACT_DOCTOR, CONTACT_EMERGENCY_CONTACT, CANCEL).
        Validates state machine transitions.
        """
        event = db.query(EmergencyEvent).filter(
            EmergencyEvent.id == event_id,
            EmergencyEvent.patient_id == patient_id
        ).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency event not found."
            )

        now = get_utc_now()

        if action == "CONTACT_DOCTOR":
            if event.status in [EmergencyStatus.RESOLVED, EmergencyStatus.CANCELLED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot initiate contact on a {event.status.value.lower()} emergency event."
                )
            event.contacted_doctor = True
            event.contacted_at = now
            if event.status == EmergencyStatus.PENDING:
                event.status = EmergencyStatus.CONTACT_INITIATED
            if notes:
                event.notes = f"{event.notes or ''}\n[Patient Note]: {notes}".strip()

        elif action == "CONTACT_EMERGENCY_CONTACT":
            if event.status in [EmergencyStatus.RESOLVED, EmergencyStatus.CANCELLED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot initiate contact on a {event.status.value.lower()} emergency event."
                )
            event.contacted_emergency_contact = True
            event.contacted_at = now
            if event.status == EmergencyStatus.PENDING:
                event.status = EmergencyStatus.CONTACT_INITIATED
            if notes:
                event.notes = f"{event.notes or ''}\n[Patient Note]: {notes}".strip()

        elif action == "CANCEL":
            if event.status in [EmergencyStatus.RESOLVED, EmergencyStatus.CANCELLED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Event is already {event.status.value.lower()}."
                )
            event.status = EmergencyStatus.CANCELLED
            if notes:
                event.notes = f"{event.notes or ''}\n[Cancellation Reason]: {notes}".strip()

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {action}"
            )

        db.commit()
        db.refresh(event)
        return EmergencyService._format_event_response(db, event)

    @staticmethod
    def doctor_take_action(
        db: Session,
        doctor_id: str,
        event_id: str,
        action: str,
        notes: Optional[str] = None
    ) -> EmergencyEventResponse:
        """
        Executes a clinician status transition (ACKNOWLEDGE, RESOLVE).
        Enforces doctor-patient assignment and state machine constraints.
        """
        event = db.query(EmergencyEvent).filter(EmergencyEvent.id == event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency event not found or access denied."
            )

        # Assignment verification
        assignment = db.query(DoctorPatient).filter(
            DoctorPatient.doctor_id == doctor_id,
            DoctorPatient.patient_id == event.patient_id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency event not found or access denied."
            )

        if action == "ACKNOWLEDGE":
            if event.status in [EmergencyStatus.RESOLVED, EmergencyStatus.CANCELLED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot acknowledge an event that is already {event.status.value.lower()}."
                )
            event.status = EmergencyStatus.ACKNOWLEDGED
            if notes:
                event.notes = f"{event.notes or ''}\n[Clinician Acknowledged]: {notes}".strip()

        elif action == "RESOLVE":
            if event.status == EmergencyStatus.CANCELLED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot resolve a cancelled event."
                )
            event.status = EmergencyStatus.RESOLVED
            if notes:
                event.notes = f"{event.notes or ''}\n[Clinician Resolution]: {notes}".strip()

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {action}"
            )

        db.commit()
        db.refresh(event)
        return EmergencyService._format_event_response(db, event)

    @staticmethod
    def get_patient_emergency_context(
        db: Session,
        patient_id: str
    ) -> EmergencyContextResponse:
        """
        Gathers contextual metadata for the patient emergency support view:
        - Emergency contact status
        - Assigned doctor details
        - Latest AI risk score & level
        - Current active emergency event (if any)
        """
        patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found."
            )

        # Assigned doctor
        assignment = db.query(DoctorPatient).filter(DoctorPatient.patient_id == patient_id).first()
        has_doc = False
        doc_name = None
        doc_spec = None
        if assignment and assignment.doctor and assignment.doctor.user:
            has_doc = True
            doc_name = f"Dr. {assignment.doctor.user.first_name} {assignment.doctor.user.last_name}"
            doc_spec = assignment.doctor.specialization

        # Latest Risk Assessment
        latest_risk = db.query(RiskAssessment).filter(
            RiskAssessment.patient_id == patient_id
        ).order_by(desc(RiskAssessment.created_at)).first()

        # Active event
        active_event = db.query(EmergencyEvent).filter(
            EmergencyEvent.patient_id == patient_id,
            EmergencyEvent.status.in_([
                EmergencyStatus.PENDING,
                EmergencyStatus.CONTACT_INITIATED,
                EmergencyStatus.ACKNOWLEDGED
            ])
        ).order_by(desc(EmergencyEvent.created_at)).first()

        active_resp = None
        if active_event:
            active_resp = EmergencyService._format_event_response(db, active_event)

        has_ec = bool(patient.emergency_contact_name and patient.emergency_contact_phone)

        return EmergencyContextResponse(
            has_emergency_contact=has_ec,
            emergency_contact_name=patient.emergency_contact_name,
            emergency_contact_phone=patient.emergency_contact_phone,
            has_assigned_doctor=has_doc,
            assigned_doctor_name=doc_name,
            assigned_doctor_specialization=doc_spec,
            latest_risk_level=latest_risk.risk_level.value if latest_risk and hasattr(latest_risk.risk_level, 'value') else str(latest_risk.risk_level) if latest_risk else None,
            latest_risk_score=latest_risk.risk_score if latest_risk else None,
            latest_risk_assessment_id=latest_risk.id if latest_risk else None,
            active_event=active_resp,
        )

    @staticmethod
    def get_static_guidance() -> EmergencyGuidanceResponse:
        """
        Returns static, non-diagnostic, safety-first emergency guidance.
        No LLM generation is used.
        """
        items = [
            EmergencyGuidanceItem(
                title="Ensure Immediate Physical Safety",
                description="If you experience severe dizziness, vertigo, or instability, immediately sit or lie down on a secure surface to prevent falls and physical injuries.",
                category="SAFETY"
            ),
            EmergencyGuidanceItem(
                title="Avoid Operating Vehicles or Machinery",
                description="Do not drive, operate motorized equipment, or perform hazardous tasks while experiencing acute dizziness, spinning sensations, or visual disturbances.",
                category="SAFETY"
            ),
            EmergencyGuidanceItem(
                title="Recognize Urgent Neurological Red Flags",
                description="Seek emergency medical services immediately if dizziness is accompanied by sudden weakness, numbness, facial droop, slurred speech, double vision, or inability to walk.",
                category="RED_FLAGS"
            ),
            EmergencyGuidanceItem(
                title="Seek Professional Medical Evaluation",
                description="VertiCare AI provides decision support metrics, not a medical diagnosis. Contact your physician or local medical emergency services for definitive clinical evaluation.",
                category="CLINICAL"
            )
        ]

        disclaimer = (
            "VertiCare AI is an academic prototype for screening and clinical decision support. "
            "It does NOT replace emergency dispatch, clinical triage, or direct physician examination. "
            "In case of immediate medical emergencies, call your local emergency medical service without delay."
        )

        return EmergencyGuidanceResponse(guidance=items, disclaimer=disclaimer)
