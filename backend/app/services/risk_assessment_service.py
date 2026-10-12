from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.risk import RiskAssessment, RiskLevel
from app.models.monitoring import DailyHealthCheck
from app.models.questionnaire import QuestionnaireSession, SessionStatus
from app.models.eye_analysis import EyeAnalysisSession, EyeAnalysisStatus
from app.models.profile import PatientProfile
from app.schemas.risk import (
    RiskAssessmentCreateRequest,
    RiskAssessmentResponse,
    RiskAssessmentListResponse,
    GeneralSymptomAssessmentRequest,
    GeneralSymptomAssessmentResponse
)
from ml.src.feature_engineering import extract_features_from_modalities
from ml.src.predict import RiskPredictor
from ml.src.general_symptom_engine.engine import GeneralSymptomRiskEngine



class RiskAssessmentService:
    @classmethod
    def evaluate_patient_risk(
        cls,
        db: Session,
        patient_id: str,
        data: RiskAssessmentCreateRequest
    ) -> RiskAssessmentResponse:
        """
        Gathers multimodal patient data, executes ML risk inference, persists the assessment,
        and returns a controlled LOW/MEDIUM/HIGH screening estimate.
        """
        # 1. Fetch Health Check Modality
        health_check = None
        if data.health_check_id:
            health_check = db.query(DailyHealthCheck).filter(
                DailyHealthCheck.id == data.health_check_id,
                DailyHealthCheck.patient_id == patient_id
            ).first()
        else:
            health_check = db.query(DailyHealthCheck).filter(
                DailyHealthCheck.patient_id == patient_id
            ).order_by(DailyHealthCheck.check_date.desc(), DailyHealthCheck.created_at.desc()).first()

        hc_dict = None
        if health_check:
            hc_dict = {
                "dizziness_severity": health_check.dizziness_severity,
                "imbalance_severity": health_check.imbalance_severity,
                "stress_level": health_check.stress_level,
                "sleep_hours": health_check.sleep_hours,
                "triggers": health_check.triggers or [],
                "episode_duration": health_check.episode_duration,
                "hydration_level": health_check.hydration_level,
                "medication_adherence": health_check.medication_adherence,
                "nausea": health_check.nausea,
                "headache": health_check.headache,
            }

        # 2. Fetch Questionnaire Modality
        q_session = None
        if data.questionnaire_session_id:
            q_session = db.query(QuestionnaireSession).filter(
                QuestionnaireSession.id == data.questionnaire_session_id,
                QuestionnaireSession.patient_id == patient_id
            ).first()
        else:
            q_session = db.query(QuestionnaireSession).filter(
                QuestionnaireSession.patient_id == patient_id,
                QuestionnaireSession.status == SessionStatus.COMPLETED
            ).order_by(QuestionnaireSession.completed_at.desc()).first()

        q_answers_list = None
        if q_session and q_session.answers:
            q_answers_list = [
                {"question_code": a.question_code, "answer": a.answer}
                for a in q_session.answers
            ]

        # 3. Fetch Eye Analysis Modality
        eye_session = None
        if data.eye_analysis_session_id:
            eye_session = db.query(EyeAnalysisSession).filter(
                EyeAnalysisSession.id == data.eye_analysis_session_id,
                EyeAnalysisSession.patient_id == patient_id
            ).first()
        else:
            eye_session = db.query(EyeAnalysisSession).filter(
                EyeAnalysisSession.patient_id == patient_id,
                EyeAnalysisSession.analysis_status == EyeAnalysisStatus.COMPLETED
            ).order_by(EyeAnalysisSession.created_at.desc()).first()

        cv_feat_dict = None
        cv_quality_dict = None
        if eye_session:
            cv_quality_dict = eye_session.quality_summary or {}
            if eye_session.features:
                cv_feat_dict = {f.feature_name: f.feature_value for f in eye_session.features}

        # Check for insufficient total input
        if not health_check and not q_session and not eye_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient clinical input data. Please complete at least one daily health check, screening questionnaire, or eye movement screening to calculate risk."
            )

        # 4. Construct Feature Vector
        feature_dict = extract_features_from_modalities(
            health_check=hc_dict,
            questionnaire_answers=q_answers_list,
            cv_features=cv_feat_dict,
            cv_quality=cv_quality_dict
        )

        # 5. Run Prediction
        try:
            pred_result = RiskPredictor.predict(feature_dict)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI risk assessment model inference failed: {str(e)}"
            )

        # 6. Persist Risk Assessment
        risk_level_enum = RiskLevel(pred_result["risk_level"])

        assessment = RiskAssessment(
            patient_id=patient_id,
            health_check_id=health_check.id if health_check else None,
            questionnaire_session_id=q_session.id if q_session else None,
            eye_analysis_session_id=eye_session.id if eye_session else None,
            risk_score=float(pred_result["risk_score"]),
            risk_level=risk_level_enum,
            model_name=pred_result["model_name"],
            model_version=pred_result["model_version"],
            contributing_factors=pred_result.get("contributing_factors", [])
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        return cls._build_response(assessment)

    @classmethod
    def get_assessment(
        cls,
        db: Session,
        patient_id: str,
        assessment_id: str
    ) -> RiskAssessmentResponse:
        """Fetch a specific risk assessment by ID with strict ownership validation."""
        assessment = db.query(RiskAssessment).filter(
            RiskAssessment.id == assessment_id,
            RiskAssessment.patient_id == patient_id
        ).first()

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk assessment not found."
            )

        return cls._build_response(assessment)

    @classmethod
    def get_history(
        cls,
        db: Session,
        patient_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> RiskAssessmentListResponse:
        """Fetch patient's own historical risk assessments ordered chronologically (newest first)."""
        query = db.query(RiskAssessment).filter(
            RiskAssessment.patient_id == patient_id
        ).order_by(RiskAssessment.created_at.desc())

        total = query.count()
        records = query.offset(offset).limit(limit).all()

        items = [cls._build_response(r) for r in records]
        return RiskAssessmentListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )

    @classmethod
    def assess_general_symptoms(
        cls,
        db: Session,
        patient_id: str,
        data: GeneralSymptomAssessmentRequest
    ) -> GeneralSymptomAssessmentResponse:
        """
        Executes experimental general symptom pattern inference using the Kaggle benchmark engine.
        Auto-populates age and gender from the patient profile when omitted.
        Enforces clear clinical boundary disclaimers that this is NOT a vertigo diagnostic tool.
        """
        patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found."
            )

        # 1. Resolve Patient Age
        age = data.age
        if age is None:
            if patient.date_of_birth:
                today = date.today()
                dob = patient.date_of_birth
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                age = 35  # reasonable fallback if DOB missing

        # 2. Resolve Patient Gender
        gender = data.gender
        if not gender:
            if patient.gender:
                g_val = patient.gender.value.upper()
                if g_val == "MALE":
                    gender = "Male"
                elif g_val == "FEMALE":
                    gender = "Female"
                else:
                    gender = "Female"
            else:
                gender = "Female"

        # 3. Assemble profile payload
        profile_dict = {
            "Fever": "Yes" if data.fever is True else ("No" if data.fever is False else "No"),
            "Cough": "Yes" if data.cough is True else ("No" if data.cough is False else "No"),
            "Fatigue": "Yes" if data.fatigue is True else ("No" if data.fatigue is False else "No"),
            "Difficulty Breathing": "Yes" if data.difficulty_breathing is True else ("No" if data.difficulty_breathing is False else "No"),
            "Age": int(age),
            "Gender": str(gender),
            "Blood Pressure": str(data.blood_pressure or "Normal"),
            "Cholesterol Level": str(data.cholesterol_level or "Normal"),
        }

        # 4. Execute inference
        res = GeneralSymptomRiskEngine.assess(profile_dict)

        return GeneralSymptomAssessmentResponse(
            assessment_type=res.assessment_type,
            model_version=res.model_version,
            status=res.status,
            prediction=res.prediction,
            probability_positive=res.probability_positive,
            confidence_tier=res.confidence_tier,
            data_quality_warnings=res.data_quality_warnings,
            insufficient_information=res.insufficient_information,
            relevant_limitations=res.relevant_limitations,
            contributing_symptoms=res.contributing_symptoms,
            notice=GeneralSymptomAssessmentResponse.model_fields["notice"].default
        )

    @staticmethod
    def _build_response(assessment: RiskAssessment) -> RiskAssessmentResponse:
        """Build RiskAssessmentResponse schema from database entity."""
        return RiskAssessmentResponse(
            id=assessment.id,
            patient_id=assessment.patient_id,
            health_check_id=assessment.health_check_id,
            questionnaire_session_id=assessment.questionnaire_session_id,
            eye_analysis_session_id=assessment.eye_analysis_session_id,
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            model_name=assessment.model_name,
            model_version=assessment.model_version,
            contributing_factors=assessment.contributing_factors or [],
            created_at=assessment.created_at
        )


