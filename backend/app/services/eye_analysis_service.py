from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.eye_analysis import (
    EyeAnalysisSession,
    EyeMovementFeature,
    EyeAnalysisStatus
)
from app.schemas.eye_analysis import (
    EyeMovementFeaturesSubmitRequest,
    EyeFeatureItem,
    EyeScreeningInterpretationResponse,
    EyeAnalysisSessionResponse
)
from app.services.eye_screening_engine import EyeScreeningEngine


class EyeAnalysisService:
    @classmethod
    def create_session(
        cls,
        db: Session,
        patient_id: str
    ) -> EyeAnalysisSessionResponse:
        """Create a new eye movement screening analysis session for the authenticated patient."""
        session = EyeAnalysisSession(
            patient_id=patient_id,
            analysis_status=EyeAnalysisStatus.RUNNING,
            quality_summary={},
            screening_result={}
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return cls._build_response(session)

    @classmethod
    def save_features(
        cls,
        db: Session,
        patient_id: str,
        session_id: str,
        data: EyeMovementFeaturesSubmitRequest
    ) -> EyeAnalysisSessionResponse:
        """
        Store validated numerical CV features, technical tracking quality indicators,
        and evidence-based screening interpretation.
        Transaction-safe and strictly bound to the authenticated patient's session.
        """
        session = db.query(EyeAnalysisSession).filter(
            EyeAnalysisSession.id == session_id,
            EyeAnalysisSession.patient_id == patient_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Eye analysis session not found."
            )

        if session.analysis_status not in (EyeAnalysisStatus.RUNNING, EyeAnalysisStatus.PENDING):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot save features to session with status '{session.analysis_status.value}'."
            )

        try:
            # Delete existing features if retried
            db.query(EyeMovementFeature).filter(
                EyeMovementFeature.session_id == session.id
            ).delete()

            for feat_name, feat_val in data.features.items():
                db_feat = EyeMovementFeature(
                    session_id=session.id,
                    feature_name=feat_name,
                    feature_value=float(feat_val)
                )
                db.add(db_feat)

            session.quality_summary = data.quality_summary.model_dump()
            session.ended_at = datetime.now(timezone.utc)

            # Generate evidence-based screening interpretation
            screening_res = EyeScreeningEngine.interpret_screening(
                features=data.features,
                quality=data.quality_summary.model_dump()
            )
            session.screening_result = screening_res.model_dump()

            if data.quality_summary.is_sufficient:
                session.analysis_status = EyeAnalysisStatus.COMPLETED
            else:
                session.analysis_status = EyeAnalysisStatus.INSUFFICIENT_QUALITY

            db.commit()
            db.refresh(session)
            return cls._build_response(session)

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to record eye movement features: {str(e)}"
            )

    @classmethod
    def get_session(
        cls,
        db: Session,
        patient_id: str,
        session_id: str
    ) -> EyeAnalysisSessionResponse:
        """Fetch an existing eye analysis session by ID with strict ownership validation."""
        session = db.query(EyeAnalysisSession).filter(
            EyeAnalysisSession.id == session_id,
            EyeAnalysisSession.patient_id == patient_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Eye analysis session not found."
            )

        return cls._build_response(session)

    @staticmethod
    def _build_response(session: EyeAnalysisSession) -> EyeAnalysisSessionResponse:
        """Map EyeAnalysisSession entity to safe EyeAnalysisSessionResponse schema."""
        feature_items = [
            EyeFeatureItem(
                id=f.id,
                feature_name=f.feature_name,
                feature_value=f.feature_value,
                created_at=f.created_at
            )
            for f in (session.features or [])
        ]

        screening = None
        if session.screening_result:
            try:
                screening = EyeScreeningInterpretationResponse.model_validate(session.screening_result)
            except Exception:
                screening = None
        elif feature_items:
            # Dynamically evaluate if not previously stored
            feat_dict = {f.feature_name: f.feature_value for f in feature_items}
            screening = EyeScreeningEngine.interpret_screening(
                features=feat_dict,
                quality=session.quality_summary or {}
            )

        return EyeAnalysisSessionResponse(
            id=session.id,
            patient_id=session.patient_id,
            started_at=session.started_at,
            ended_at=session.ended_at,
            analysis_status=session.analysis_status,
            quality_summary=session.quality_summary or {},
            features=feature_items,
            screening=screening,
            created_at=session.created_at
        )
