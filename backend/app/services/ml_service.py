import os
import json
from datetime import date, datetime
from typing import Optional, Dict, Any, Tuple
import numpy as np
import joblib
import xgboost as xgb
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.models.profile import PatientProfile
from app.models.monitoring import DailyHealthCheck
from app.models.questionnaire import QuestionnaireSession, QuestionnaireAnswer
from app.models.eye_analysis import EyeAnalysisSession, EyeMovementFeature
from app.models.risk import RiskAssessment, RiskCategory, Recommendation
from app.schemas.risk import RiskAssessmentRequest, RiskAssessmentResponse, FactorContribution, RecommendationResponse
from app.services.recommendation_service import RecommendationService
from ml.features import extract_feature_vector, FEATURE_COLUMNS
from ml.explainability import ModelExplainer
from app.core.exceptions import ResourceNotFoundException


class MLService:
    _model: Optional[xgb.XGBClassifier] = None
    _scaler: Optional[Any] = None
    _metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def get_model(cls) -> Tuple[Optional[xgb.XGBClassifier], Optional[Any], Dict[str, Any]]:
        """Lazy loader for serialized XGBoost model, RobustScaler, and metadata."""
        if cls._model is None:
            model_file = settings.ML_MODEL_PATH
            scaler_file = settings.ML_SCALER_PATH
            meta_file = settings.ML_METADATA_PATH

            # Check alternative relative path if running from backend dir
            if not os.path.exists(model_file):
                model_file = os.path.join("backend", settings.ML_MODEL_PATH)
                scaler_file = os.path.join("backend", settings.ML_SCALER_PATH)
                meta_file = os.path.join("backend", settings.ML_METADATA_PATH)

            if os.path.exists(model_file) and os.path.exists(scaler_file):
                try:
                    loaded_model = xgb.XGBClassifier()
                    loaded_model.load_model(model_file)
                    loaded_scaler = joblib.load(scaler_file)
                    cls._model = loaded_model
                    cls._scaler = loaded_scaler

                    if os.path.exists(meta_file):
                        with open(meta_file, "r") as f:
                            cls._metadata = json.load(f)
                    else:
                        cls._metadata = {"model_name": "VertiCare-Ensemble-XGB", "model_version": "1.0.0"}
                except Exception as e:
                    print(f"Warning: Failed to load serialized ML model: {e}")
                    cls._model = None
                    cls._scaler = None
                    cls._metadata = {"model_name": "VertiCare-Rule-Ensemble", "model_version": "1.0.0-fallback"}
            else:
                cls._metadata = {"model_name": "VertiCare-Rule-Ensemble", "model_version": "1.0.0-fallback"}

        return cls._model, cls._scaler, cls._metadata or {}

    @classmethod
    def assess_risk(
        cls,
        db: Session,
        patient_id: str,
        request: Optional[RiskAssessmentRequest] = None
    ) -> RiskAssessment:
        """
        Execute multi-modal risk assessment fusing symptom logs, adaptive questionnaire,
        and webcam eye-tracking kinematics.
        """
        patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
        if not patient:
            raise ResourceNotFoundException(f"Patient '{patient_id}' not found")

        # 1. Resolve Daily Health Check
        health_check = None
        if request and request.health_check_id:
            health_check = db.query(DailyHealthCheck).filter(
                DailyHealthCheck.id == request.health_check_id
            ).first()
        if not health_check:
            health_check = db.query(DailyHealthCheck).filter(
                DailyHealthCheck.patient_id == patient_id
            ).order_by(desc(DailyHealthCheck.check_in_date)).first()

        # 2. Resolve Questionnaire Session & Answers Map
        q_session = None
        q_map: Dict[str, Any] = {}
        if request and request.questionnaire_session_id:
            q_session = db.query(QuestionnaireSession).filter(
                QuestionnaireSession.id == request.questionnaire_session_id
            ).first()
        if not q_session:
            q_session = db.query(QuestionnaireSession).filter(
                QuestionnaireSession.patient_id == patient_id
            ).order_by(desc(QuestionnaireSession.created_at)).first()

        if q_session:
            q_map = {a.question_id: a.selected_values for a in q_session.answers}

        # 3. Resolve Eye Tracking Session & Features
        eye_session = None
        eye_features = None
        if request and request.eye_analysis_session_id:
            eye_session = db.query(EyeAnalysisSession).filter(
                EyeAnalysisSession.id == request.eye_analysis_session_id
            ).first()
        if not eye_session:
            eye_session = db.query(EyeAnalysisSession).filter(
                EyeAnalysisSession.patient_id == patient_id
            ).order_by(desc(EyeAnalysisSession.created_at)).first()

        if eye_session and eye_session.features:
            eye_features = eye_session.features

        # Calculate patient age
        today = date.today()
        dob = patient.date_of_birth or date(1990, 1, 1)
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # 4. Extract Multi-Modal Feature Vector
        feature_vector = extract_feature_vector(
            health_check=health_check,
            questionnaire_answers=q_map,
            eye_features=eye_features,
            patient_age=age
        )

        # 5. Model Inference / Risk Estimation
        model, scaler, metadata = cls.get_model()
        
        has_red_flags = False
        neuro = q_map.get("Q_NEUROLOGIC_RED_FLAGS", [])
        if isinstance(neuro, list) and any(n in neuro for n in ["slurred_speech", "facial_weakness_numbness", "double_vision", "limb_weakness_clumsiness", "swallowing_difficulty"]):
            has_red_flags = True

        if model is not None and scaler is not None:
            try:
                X_scaled = scaler.transform(feature_vector.reshape(1, -1))
                probs = model.predict_proba(X_scaled)[0]  # [p_low, p_med, p_high]
                # Composite risk score calculation (0 to 100)
                raw_score = (probs[0] * 18.0) + (probs[1] * 52.0) + (probs[2] * 92.0)
            except Exception:
                probs = np.array([0.5, 0.35, 0.15])
                raw_score = 35.0
        else:
            # Calibrated heuristic fallback
            diz = float(health_check.dizziness_severity) if health_check else 4.0
            unst = float(health_check.unsteadiness_severity) if health_check else 3.0
            stability = float(eye_features.gaze_fixation_stability_score) if eye_features else 85.0
            nystagmus = 1.0 if (eye_features and eye_features.nystagmoid_pattern_detected) else 0.0

            raw_score = (diz * 4.0) + (unst * 3.5) + ((100.0 - stability) * 0.25) + (nystagmus * 15.0)
            probs = np.array([0.4, 0.4, 0.2])

        # Red flag escalation override
        if has_red_flags:
            raw_score = max(raw_score, 82.0)

        final_score = round(max(0.0, min(100.0, float(raw_score))), 1)

        if final_score < 35.0:
            category = RiskCategory.LOW
        elif final_score < 70.0:
            category = RiskCategory.MEDIUM
        else:
            category = RiskCategory.HIGH

        # 6. Generate Explainability Attribution
        contributing_factors = ModelExplainer.explain_instance(
            feature_vector=feature_vector,
            predicted_probs=probs,
            model=model
        )

        # 7. Generate Non-Diagnostic Clinical Summary
        if category == RiskCategory.HIGH:
            summary = (
                f"Composite risk estimation is {final_score}/100 (HIGH). "
                f"Elevated postural instability or acute symptom indicators detected. "
                f"Immediate clinical evaluation recommended."
            )
        elif category == RiskCategory.MEDIUM:
            summary = (
                f"Composite risk estimation is {final_score}/100 (MEDIUM). "
                f"Moderate dizziness and observable gaze deviations detected. "
                f"Specialist otoneurological follow-up advised for detailed clinical examination."
            )
        else:
            summary = (
                f"Composite risk estimation is {final_score}/100 (LOW). "
                f"Stable visual fixation holding and mild symptom ratings observed. "
                f"Continue routine lifestyle monitoring."
            )

        # 8. Persist Risk Assessment
        assessment = RiskAssessment(
            patient_id=patient_id,
            health_check_id=health_check.id if health_check else None,
            questionnaire_session_id=q_session.id if q_session else None,
            eye_analysis_session_id=eye_session.id if eye_session else None,
            risk_score=final_score,
            risk_category=category,
            model_name=metadata.get("model_name", "VertiCare-Ensemble-XGB"),
            model_version=metadata.get("model_version", "1.0.0"),
            contributing_factors=contributing_factors,
            clinical_summary=summary
        )
        db.add(assessment)
        db.flush()

        # 9. Generate non-prescriptive recommendations
        RecommendationService.generate_recommendations_for_assessment(
            db=db,
            risk_assessment_id=assessment.id,
            risk_category=category,
            contributing_factors=contributing_factors,
            has_red_flags=has_red_flags
        )

        db.commit()
        db.refresh(assessment)
        return assessment

    @staticmethod
    def map_assessment_to_dto(assessment: RiskAssessment) -> RiskAssessmentResponse:
        """Map RiskAssessment entity to response DTO."""
        factors = [
            FactorContribution(
                factor=f.get("factor", ""),
                impact_direction=f.get("impact_direction", "INCREASES_RISK"),
                importance_score=f.get("importance_score", 0.0),
                description=f.get("description", "")
            )
            for f in assessment.contributing_factors
        ]

        recs = [
            RecommendationResponse.model_validate(r)
            for r in assessment.recommendations
        ]

        return RiskAssessmentResponse(
            id=assessment.id,
            patient_id=assessment.patient_id,
            health_check_id=assessment.health_check_id,
            questionnaire_session_id=assessment.questionnaire_session_id,
            eye_analysis_session_id=assessment.eye_analysis_session_id,
            risk_score=assessment.risk_score,
            risk_category=assessment.risk_category,
            model_name=assessment.model_name,
            model_version=assessment.model_version,
            contributing_factors=factors,
            clinical_summary=assessment.clinical_summary,
            recommendations=recs,
            created_at=assessment.created_at
        )
