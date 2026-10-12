import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Union, Dict, Any
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
from cv.src.pipeline import CVPipeline


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
    def process_video(
        cls,
        db: Session,
        patient_id: str,
        session_id: str,
        video_path: Union[str, Path],
        max_frames: int = 300,
        max_duration_sec: float = 30.0
    ) -> EyeAnalysisSessionResponse:
        """
        Processes an uploaded eye-tracking video file end-to-end:
        1. Validates session ownership and active status.
        2. Executes CVPipeline to extract frame-by-frame landmarks, RANSAC pupil fit, and oscillatory kinematics.
        3. Persists extracted numerical features into EyeMovementFeature entities.
        4. Evaluates evidence-based screening interpretation.
        5. Updates session status to COMPLETED (or INSUFFICIENT_QUALITY).
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
                detail=f"Cannot process video for session with status '{session.analysis_status.value}'."
            )

        pipeline = CVPipeline(session_id=session.id)
        cv_result = pipeline.process_video_file(
            video_path,
            max_frames=max_frames,
            max_duration_sec=max_duration_sec
        )

        if cv_result.status == "FAILED":
            session.analysis_status = EyeAnalysisStatus.FAILED
            session.quality_summary = cv_result.quality.to_dict()
            session.ended_at = datetime.now(timezone.utc)
            session.screening_result = {
                "status": "UNAVAILABLE",
                "label": "VIDEO_PROCESSING_FAILED",
                "explanation": " ".join(cv_result.warnings) or "Failed to process video file."
            }
            db.commit()
            db.refresh(session)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Video processing failed: {'; '.join(cv_result.warnings)}"
            )

        try:
            # Delete previous features if retrying
            db.query(EyeMovementFeature).filter(
                EyeMovementFeature.session_id == session.id
            ).delete()

            # Persist extracted movement features
            for feat_name, feat_val in cv_result.features.to_dict().items():
                db_feat = EyeMovementFeature(
                    session_id=session.id,
                    feature_name=feat_name,
                    feature_value=float(feat_val)
                )
                db.add(db_feat)

            # Store quality summary and video metadata
            quality_data = cv_result.quality.to_dict()
            if cv_result.video_metadata:
                quality_data["video_metadata"] = cv_result.video_metadata.to_dict()
            session.quality_summary = quality_data
            session.ended_at = datetime.now(timezone.utc)

            # Run screening interpretation with kinematics
            screening_res = EyeScreeningEngine.interpret_screening(
                features=cv_result.features.to_dict(),
                quality=cv_result.quality.to_dict(),
                nystagmus_analysis=cv_result.nystagmus_analysis
            )
            session.screening_result = screening_res.model_dump()

            if cv_result.quality.is_sufficient:
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
                detail=f"Failed to record video eye movement features: {str(e)}"
            )

    @classmethod
    def process_sample_video(
        cls,
        db: Session,
        patient_id: str,
        pattern: str = "normal"
    ) -> EyeAnalysisSessionResponse:
        """
        Generates and processes a synthetic sample eye-movement video matching a specific kinematic pattern
        ('normal', 'horizontal_nystagmus', or 'vertical_nystagmus') through the real CVPipeline.
        """
        import tempfile
        from cv.src.capture import SyntheticFrameGenerator

        session_resp = cls.create_session(db, patient_id)
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_path = temp_file.name
        temp_file.close()

        try:
            SyntheticFrameGenerator.create_synthetic_test_video(
                output_path=temp_path,
                duration_sec=3.0,
                fps=30.0,
                pattern=pattern
            )
            return cls.process_video(
                db=db,
                patient_id=patient_id,
                session_id=session_resp.id,
                video_path=temp_path,
                max_frames=300,
                max_duration_sec=30.0
            )
        finally:
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

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

        video_meta = None
        if session.quality_summary and isinstance(session.quality_summary, dict):
            video_meta = session.quality_summary.get("video_metadata")

        return EyeAnalysisSessionResponse(
            id=session.id,
            patient_id=session.patient_id,
            started_at=session.started_at,
            ended_at=session.ended_at,
            analysis_status=session.analysis_status,
            quality_summary=session.quality_summary or {},
            features=feature_items,
            screening=screening,
            video_metadata=video_meta,
            created_at=session.created_at
        )

