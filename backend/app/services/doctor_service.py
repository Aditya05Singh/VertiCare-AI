from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException, status

from app.models.user import User
from app.models.profile import PatientProfile, DoctorProfile, DoctorPatient
from app.models.monitoring import DailyHealthCheck
from app.models.questionnaire import QuestionnaireSession, QuestionnaireQuestion, SessionStatus
from app.models.eye_analysis import EyeAnalysisSession, EyeMovementFeature, EyeAnalysisStatus
from app.models.risk import RiskAssessment, RiskLevel
from app.models.clinical import DoctorNote, NoteType
from app.schemas.doctor import (
    DoctorDashboardSummaryResponse,
    DoctorRecentActivityItem,
    AssignedPatientCardResponse,
    DoctorPatientListResponse,
    DoctorPatientDossierResponse,
    DoctorNoteCreateRequest,
    DoctorNoteUpdateRequest,
    DoctorNoteResponse,
    DoctorPatientReportResponse
)
from app.schemas.monitoring import (
    DailyHealthCheckResponse,
    DailyHealthCheckListResponse,
    DailyHealthTrendResponse
)
from app.schemas.questionnaire import SessionSummaryResponse, AnswerSummaryItem
from app.schemas.eye_analysis import EyeAnalysisSessionResponse, QualitySummarySchema, EyeFeatureItem
from app.schemas.risk import RiskAssessmentResponse, RiskAssessmentListResponse
from app.services.health_check_service import HealthCheckService
from app.services.risk_assessment_service import RiskAssessmentService
from app.services.eye_analysis_service import EyeAnalysisService
from app.services.questionnaire_service import QuestionnaireService


class DoctorService:
    @staticmethod
    def get_dashboard_summary(
        db: Session,
        doctor_id: str
    ) -> DoctorDashboardSummaryResponse:
        """Calculates real clinician dashboard summary statistics from assigned patients only."""
        assignments = db.query(DoctorPatient).filter(DoctorPatient.doctor_id == doctor_id).all()
        assigned_patient_ids = [a.patient_id for a in assignments]
        total_assigned = len(assigned_patient_ids)

        risk_distribution = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNASSESSED": 0}
        recent_activities: List[DoctorRecentActivityItem] = []

        if total_assigned == 0:
            return DoctorDashboardSummaryResponse(
                total_assigned_patients=0,
                risk_distribution=risk_distribution,
                recent_activity=[]
            )

        for a in assignments:
            patient = a.patient
            user = patient.user if patient else None
            patient_name = f"{user.first_name} {user.last_name}" if user else "Patient"

            # Latest Risk Assessment
            latest_risk = db.query(RiskAssessment).filter(
                RiskAssessment.patient_id == a.patient_id
            ).order_by(RiskAssessment.created_at.desc()).first()

            if latest_risk:
                risk_key = latest_risk.risk_level.value
                risk_distribution[risk_key] = risk_distribution.get(risk_key, 0) + 1
            else:
                risk_distribution["UNASSESSED"] += 1

            # Check for recent health checks
            recent_hc = db.query(DailyHealthCheck).filter(
                DailyHealthCheck.patient_id == a.patient_id
            ).order_by(DailyHealthCheck.created_at.desc()).first()
            if recent_hc:
                recent_activities.append(
                    DoctorRecentActivityItem(
                        patient_id=a.patient_id,
                        patient_name=patient_name,
                        activity_type="HEALTH_CHECK",
                        timestamp=recent_hc.created_at,
                        description=f"Logged daily symptoms (Dizziness: {recent_hc.dizziness_severity}/10, Imbalance: {recent_hc.imbalance_severity}/10)",
                        risk_level=latest_risk.risk_level.value if latest_risk else None
                    )
                )

            # Check for recent completed questionnaires
            recent_q = db.query(QuestionnaireSession).filter(
                QuestionnaireSession.patient_id == a.patient_id,
                QuestionnaireSession.status == SessionStatus.COMPLETED
            ).order_by(QuestionnaireSession.completed_at.desc()).first()
            if recent_q and recent_q.completed_at:
                recent_activities.append(
                    DoctorRecentActivityItem(
                        patient_id=a.patient_id,
                        patient_name=patient_name,
                        activity_type="QUESTIONNAIRE",
                        timestamp=recent_q.completed_at,
                        description="Completed adaptive screening questionnaire",
                        risk_level=latest_risk.risk_level.value if latest_risk else None
                    )
                )

            # Check for recent completed eye sessions
            recent_eye = db.query(EyeAnalysisSession).filter(
                EyeAnalysisSession.patient_id == a.patient_id,
                EyeAnalysisSession.analysis_status == EyeAnalysisStatus.COMPLETED
            ).order_by(EyeAnalysisSession.created_at.desc()).first()
            if recent_eye:
                recent_activities.append(
                    DoctorRecentActivityItem(
                        patient_id=a.patient_id,
                        patient_name=patient_name,
                        activity_type="EYE_ANALYSIS",
                        timestamp=recent_eye.created_at,
                        description="Completed webcam eye-movement screening session",
                        risk_level=latest_risk.risk_level.value if latest_risk else None
                    )
                )

            # Check for recent risk assessments
            if latest_risk:
                recent_activities.append(
                    DoctorRecentActivityItem(
                        patient_id=a.patient_id,
                        patient_name=patient_name,
                        activity_type="RISK_ASSESSMENT",
                        timestamp=latest_risk.created_at,
                        description=f"AI screening risk evaluated as {latest_risk.risk_level.value} (Score: {latest_risk.risk_score:.2f})",
                        risk_level=latest_risk.risk_level.value
                    )
                )

        # Sort activities descending by timestamp
        recent_activities.sort(key=lambda x: x.timestamp, reverse=True)

        return DoctorDashboardSummaryResponse(
            total_assigned_patients=total_assigned,
            risk_distribution=risk_distribution,
            recent_activity=recent_activities[:15]
        )

    @staticmethod
    def get_assigned_patients(
        db: Session,
        doctor_id: str,
        search: Optional[str] = None,
        risk_filter: Optional[str] = None,
        sort_by: str = "recent"
    ) -> DoctorPatientListResponse:
        """Retrieves authorized assigned patients with search, risk filters, and sorting."""
        assignments = db.query(DoctorPatient).filter(DoctorPatient.doctor_id == doctor_id).all()
        cards: List[AssignedPatientCardResponse] = []

        for a in assignments:
            patient = a.patient
            if not patient or not patient.user:
                continue
            user = patient.user
            full_name = f"{user.first_name} {user.last_name}"

            # Apply Search filter (name or email)
            if search:
                query_lower = search.strip().lower()
                if query_lower not in full_name.lower() and query_lower not in user.email.lower():
                    continue

            # Latest Risk Assessment
            latest_risk = db.query(RiskAssessment).filter(
                RiskAssessment.patient_id == patient.id
            ).order_by(RiskAssessment.created_at.desc()).first()

            latest_risk_level = latest_risk.risk_level.value if latest_risk else None
            latest_risk_score = latest_risk.risk_score if latest_risk else None
            latest_risk_date = latest_risk.created_at if latest_risk else None

            # Apply Risk filter
            if risk_filter:
                rf_upper = risk_filter.strip().upper()
                if rf_upper in ("LOW", "MEDIUM", "HIGH"):
                    if latest_risk_level != rf_upper:
                        continue
                elif rf_upper == "UNASSESSED":
                    if latest_risk_level is not None:
                        continue

            # Latest Daily Health Check
            latest_hc = db.query(DailyHealthCheck).filter(
                DailyHealthCheck.patient_id == patient.id
            ).order_by(DailyHealthCheck.check_date.desc()).first()

            total_hcs = db.query(DailyHealthCheck).filter(
                DailyHealthCheck.patient_id == patient.id
            ).count()

            cards.append(
                AssignedPatientCardResponse(
                    patient_id=patient.id,
                    full_name=full_name,
                    email=user.email,
                    date_of_birth=patient.date_of_birth,
                    gender=patient.gender.value,
                    assigned_at=a.assigned_at,
                    latest_risk_level=latest_risk_level,
                    latest_risk_score=latest_risk_score,
                    latest_assessment_date=latest_risk_date,
                    latest_health_check_date=latest_hc.check_date if latest_hc else None,
                    latest_health_check_dizziness=latest_hc.dizziness_severity if latest_hc else None,
                    total_health_checks=total_hcs
                )
            )

        # Sorting logic
        if sort_by == "risk_high_to_low":
            risk_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, None: 0}
            cards.sort(key=lambda c: (risk_order.get(c.latest_risk_level, 0), c.latest_risk_score or 0.0), reverse=True)
        elif sort_by == "name":
            cards.sort(key=lambda c: c.full_name.lower())
        else:  # "recent"
            cards.sort(key=lambda c: c.assigned_at, reverse=True)

        return DoctorPatientListResponse(items=cards, total=len(cards))

    @staticmethod
    def get_patient_dossier(
        db: Session,
        patient: PatientProfile
    ) -> DoctorPatientDossierResponse:
        """Retrieves patient summary dossier for authorized clinicians."""
        user = patient.user
        full_name = f"{user.first_name} {user.last_name}" if user else "Patient"

        # Latest Health Check
        latest_hc = db.query(DailyHealthCheck).filter(
            DailyHealthCheck.patient_id == patient.id
        ).order_by(DailyHealthCheck.check_date.desc(), DailyHealthCheck.created_at.desc()).first()

        hc_dto = DailyHealthCheckResponse.model_validate(latest_hc) if latest_hc else None

        # Latest Questionnaire Session
        latest_q = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.patient_id == patient.id,
            QuestionnaireSession.status == SessionStatus.COMPLETED
        ).order_by(QuestionnaireSession.completed_at.desc()).first()

        q_summary = QuestionnaireService.get_session_summary(db, patient.id, latest_q.id) if latest_q else None

        # Latest Eye Analysis Session
        latest_eye = db.query(EyeAnalysisSession).filter(
            EyeAnalysisSession.patient_id == patient.id,
            EyeAnalysisSession.analysis_status == EyeAnalysisStatus.COMPLETED
        ).order_by(EyeAnalysisSession.created_at.desc()).first()

        eye_dto = EyeAnalysisService._build_response(latest_eye) if latest_eye else None

        # Latest Risk Assessment
        latest_risk = db.query(RiskAssessment).filter(
            RiskAssessment.patient_id == patient.id
        ).order_by(RiskAssessment.created_at.desc()).first()

        risk_dto = RiskAssessmentResponse.model_validate(latest_risk) if latest_risk else None

        # Notes count
        notes_count = db.query(DoctorNote).filter(DoctorNote.patient_id == patient.id).count()

        return DoctorPatientDossierResponse(
            patient_id=patient.id,
            full_name=full_name,
            email=user.email if user else "",
            date_of_birth=patient.date_of_birth,
            gender=patient.gender.value,
            medical_history=patient.medical_history,
            emergency_contact_name=patient.emergency_contact_name,
            emergency_contact_phone=patient.emergency_contact_phone,
            latest_health_check=hc_dto,
            latest_questionnaire=q_summary,
            latest_eye_analysis=eye_dto,
            latest_risk_assessment=risk_dto,
            recent_notes_count=notes_count
        )

    @staticmethod
    def get_patient_health_history(
        db: Session,
        patient_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> DailyHealthCheckListResponse:
        """Retrieves paginated daily health check history for an assigned patient."""
        items, total = HealthCheckService.get_patient_history(db, patient_id, limit, offset)
        dtos = [DailyHealthCheckResponse.model_validate(i) for i in items]
        return DailyHealthCheckListResponse(items=dtos, total=total, limit=limit, offset=offset)

    @staticmethod
    def get_patient_health_trends(
        db: Session,
        patient_id: str,
        days: int = 14
    ) -> DailyHealthTrendResponse:
        """Calculates multi-day health trends for an assigned patient."""
        return HealthCheckService.get_patient_trends(db, patient_id, days)

    @staticmethod
    def get_patient_questionnaire_history(
        db: Session,
        patient_id: str
    ) -> List[SessionSummaryResponse]:
        """Retrieves completed questionnaire sessions and answer summaries."""
        sessions = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.patient_id == patient_id,
            QuestionnaireSession.status == SessionStatus.COMPLETED
        ).order_by(QuestionnaireSession.completed_at.desc()).all()

        return [
            QuestionnaireService.get_session_summary(db, patient_id, sess.id)
            for sess in sessions
        ]

    @staticmethod
    def get_patient_eye_analysis_history(
        db: Session,
        patient_id: str
    ) -> List[EyeAnalysisSessionResponse]:
        """Retrieves eye movement screening sessions and technical features."""
        from app.services.eye_analysis_service import EyeAnalysisService
        sessions = db.query(EyeAnalysisSession).filter(
            EyeAnalysisSession.patient_id == patient_id
        ).order_by(EyeAnalysisSession.created_at.desc()).all()

        return [EyeAnalysisService._build_response(s) for s in sessions]

    @staticmethod
    def get_patient_risk_history(
        db: Session,
        patient_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> RiskAssessmentListResponse:
        """Retrieves AI screening risk assessment history for an assigned patient."""
        return RiskAssessmentService.get_history(db, patient_id, limit, offset)

    @staticmethod
    def get_patient_notes(
        db: Session,
        patient_id: str
    ) -> List[DoctorNoteResponse]:
        """Retrieves clinical notes authored for the assigned patient."""
        notes = db.query(DoctorNote).filter(
            DoctorNote.patient_id == patient_id
        ).order_by(DoctorNote.created_at.desc()).all()

        responses: List[DoctorNoteResponse] = []
        for n in notes:
            doc = n.doctor
            doc_user = doc.user if doc else None
            doc_name = f"Dr. {doc_user.first_name} {doc_user.last_name}" if doc_user else "Clinician"
            doc_spec = doc.specialization if doc else "Otolaryngology"

            responses.append(
                DoctorNoteResponse(
                    id=n.id,
                    patient_id=n.patient_id,
                    doctor_id=n.doctor_id,
                    doctor_name=doc_name,
                    doctor_specialization=doc_spec,
                    risk_assessment_id=n.risk_assessment_id,
                    note_type=n.note_type,
                    content=n.content,
                    is_shared_with_patient=n.is_shared_with_patient,
                    created_at=n.created_at,
                    updated_at=n.updated_at
                )
            )
        return responses

    @staticmethod
    def create_patient_note(
        db: Session,
        doctor: DoctorProfile,
        patient_id: str,
        data: DoctorNoteCreateRequest
    ) -> DoctorNoteResponse:
        """Authors a clinical decision support review note for an assigned patient."""
        note = DoctorNote(
            patient_id=patient_id,
            doctor_id=doctor.id,
            risk_assessment_id=data.risk_assessment_id,
            note_type=data.note_type,
            content=data.content.strip(),
            is_shared_with_patient=data.is_shared_with_patient
        )
        db.add(note)
        db.commit()
        db.refresh(note)

        doc_user = doctor.user
        doc_name = f"Dr. {doc_user.first_name} {doc_user.last_name}" if doc_user else "Clinician"

        return DoctorNoteResponse(
            id=note.id,
            patient_id=note.patient_id,
            doctor_id=note.doctor_id,
            doctor_name=doc_name,
            doctor_specialization=doctor.specialization,
            risk_assessment_id=note.risk_assessment_id,
            note_type=note.note_type,
            content=note.content,
            is_shared_with_patient=note.is_shared_with_patient,
            created_at=note.created_at,
            updated_at=note.updated_at
        )

    @staticmethod
    def update_doctor_note(
        db: Session,
        doctor_id: str,
        note_id: str,
        data: DoctorNoteUpdateRequest
    ) -> DoctorNoteResponse:
        """Updates an existing clinical note. Only the authoring clinician may edit their note."""
        note = db.query(DoctorNote).filter(DoctorNote.id == note_id).first()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clinical note not found."
            )

        if note.doctor_id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access restricted: You may only modify clinical notes authored by yourself."
            )

        note.content = data.content.strip()
        if data.note_type is not None:
            note.note_type = data.note_type
        if data.is_shared_with_patient is not None:
            note.is_shared_with_patient = data.is_shared_with_patient

        db.commit()
        db.refresh(note)

        doc = note.doctor
        doc_user = doc.user if doc else None
        doc_name = f"Dr. {doc_user.first_name} {doc_user.last_name}" if doc_user else "Clinician"
        doc_spec = doc.specialization if doc else "Otolaryngology"

        return DoctorNoteResponse(
            id=note.id,
            patient_id=note.patient_id,
            doctor_id=note.doctor_id,
            doctor_name=doc_name,
            doctor_specialization=doc_spec,
            risk_assessment_id=note.risk_assessment_id,
            note_type=note.note_type,
            content=note.content,
            is_shared_with_patient=note.is_shared_with_patient,
            created_at=note.created_at,
            updated_at=note.updated_at
        )

    @staticmethod
    def get_patient_report_summary(
        db: Session,
        patient: PatientProfile
    ) -> DoctorPatientReportResponse:
        """Compiles an aggregated multimodal clinical report summary."""
        user = patient.user
        patient_name = f"{user.first_name} {user.last_name}" if user else "Patient"

        # 14-day health check metrics
        trend = HealthCheckService.get_patient_trends(db, patient.id, days=14)
        health_summary = {
            "total_records_14d": trend.total_records,
            "average_dizziness": trend.average_dizziness,
            "average_imbalance": trend.average_imbalance,
            "average_sleep": trend.average_sleep,
            "average_stress": trend.average_stress
        }

        # Latest completed questionnaire
        latest_q = db.query(QuestionnaireSession).filter(
            QuestionnaireSession.patient_id == patient.id,
            QuestionnaireSession.status == SessionStatus.COMPLETED
        ).order_by(QuestionnaireSession.completed_at.desc()).first()

        q_summary = None
        if latest_q:
            q_summary = {
                "session_id": latest_q.id,
                "completed_at": latest_q.completed_at.isoformat() if latest_q.completed_at else None,
                "answers": [
                    {
                        "question_code": a.question_code,
                        "question_text": a.question.question_text if a.question else a.question_code,
                        "answer": a.answer
                    }
                    for a in latest_q.answers
                ]
            }

        # Latest completed eye analysis
        latest_eye = db.query(EyeAnalysisSession).filter(
            EyeAnalysisSession.patient_id == patient.id,
            EyeAnalysisSession.analysis_status == EyeAnalysisStatus.COMPLETED
        ).order_by(EyeAnalysisSession.created_at.desc()).first()

        eye_summary = None
        if latest_eye:
            eye_summary = {
                "session_id": latest_eye.id,
                "created_at": latest_eye.created_at.isoformat(),
                "quality": latest_eye.quality_summary,
                "features": {f.feature_name: f.feature_value for f in latest_eye.features}
            }

        # Latest Risk Assessment
        latest_risk = db.query(RiskAssessment).filter(
            RiskAssessment.patient_id == patient.id
        ).order_by(RiskAssessment.created_at.desc()).first()
        risk_dto = RiskAssessmentResponse.model_validate(latest_risk) if latest_risk else None

        # Clinical notes
        notes = DoctorService.get_patient_notes(db, patient.id)

        return DoctorPatientReportResponse(
            patient_id=patient.id,
            patient_name=patient_name,
            generated_at=datetime.now(timezone.utc),
            health_summary=health_summary,
            questionnaire_summary=q_summary,
            eye_analysis_summary=eye_summary,
            latest_risk=risk_dto,
            clinical_notes=notes,
            disclaimer="AI-assisted screening and decision support information — not a medical diagnosis."
        )
