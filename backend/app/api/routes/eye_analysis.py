import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_patient
from app.models.user import User
from app.schemas.eye_analysis import (
    EyeMovementFeaturesSubmitRequest,
    EyeAnalysisSessionResponse
)
from app.services.eye_analysis_service import EyeAnalysisService
from cv.src.capture import SUPPORTED_VIDEO_EXTENSIONS

router = APIRouter(prefix="/eye-analysis", tags=["Computer Vision Eye Movement Screening"])

MAX_UPLOAD_SIZE_BYTES = 150 * 1024 * 1024  # 150MB limit


def _save_upload_to_temp(file: UploadFile) -> str:
    """Safely streams UploadFile to a temporary file while enforcing extension and size limits."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported video file format '{suffix}'. Supported extensions: {sorted(list(SUPPORTED_VIDEO_EXTENSIONS))}"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        temp_path = tmp.name
        bytes_written = 0
        while True:
            chunk = file.file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            bytes_written += len(chunk)
            if bytes_written > MAX_UPLOAD_SIZE_BYTES:
                tmp.close()
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Uploaded file exceeds maximum allowed size of 150MB."
                )
            tmp.write(chunk)
    return temp_path



def _get_patient_id(current_user: User) -> str:
    if not current_user.patient_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have an active patient profile."
        )
    return current_user.patient_profile.id


@router.post(
    "/sessions",
    response_model=EyeAnalysisSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create eye-movement analysis session"
)
def create_eye_analysis_session(
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Initializes a new computer-vision screening session for the authenticated patient."""
    patient_id = _get_patient_id(current_user)
    return EyeAnalysisService.create_session(db, patient_id)


@router.post(
    "/sessions/{session_id}/features",
    response_model=EyeAnalysisSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Save extracted numerical CV eye movement features"
)
def save_eye_movement_features(
    session_id: str,
    data: EyeMovementFeaturesSubmitRequest,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Persists validated numerical CV features (amplitudes, velocities, blinks, quality scores)."""
    patient_id = _get_patient_id(current_user)
    return EyeAnalysisService.save_features(db, patient_id, session_id, data)


@router.get(
    "/sessions/{session_id}",
    response_model=EyeAnalysisSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get eye-movement session details and features"
)
def get_eye_analysis_session(
    session_id: str,
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """Fetch an eye analysis session by ID with strict patient ownership check."""
    patient_id = _get_patient_id(current_user)
    return EyeAnalysisService.get_session(db, patient_id, session_id)


@router.post(
    "/sessions/{session_id}/video",
    response_model=EyeAnalysisSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and process eye-tracking video file for an existing session"
)
def process_session_video(
    session_id: str,
    file: UploadFile = File(..., description="Uploaded video file (.mp4, .avi, .mov, .webm)"),
    max_frames: int = Query(300, ge=10, le=1000, description="Upper bound on processed frames"),
    max_duration_sec: float = Query(30.0, ge=1.0, le=60.0, description="Upper bound on video duration"),
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """
    Uploads and processes an eye-movement screening video file for an existing session.
    Extracts ocular landmarks, RANSAC pupil fit, oscillation kinematics, and screening classification.
    Cleans up all temporary disk artifacts upon completion.
    """
    patient_id = _get_patient_id(current_user)
    temp_path = _save_upload_to_temp(file)
    try:
        return EyeAnalysisService.process_video(
            db=db,
            patient_id=patient_id,
            session_id=session_id,
            video_path=temp_path,
            max_frames=max_frames,
            max_duration_sec=max_duration_sec
        )
    finally:
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass


@router.post(
    "/video-screening",
    response_model=EyeAnalysisSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="All-in-one video screening: creates session, extracts features, runs kinematics"
)
def create_and_process_video_screening(
    file: UploadFile = File(..., description="Uploaded video file (.mp4, .avi, .mov, .webm)"),
    max_frames: int = Query(300, ge=10, le=1000, description="Upper bound on processed frames"),
    max_duration_sec: float = Query(30.0, ge=1.0, le=60.0, description="Upper bound on video duration"),
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """
    Single-step video screening endpoint:
    1. Initializes a new session.
    2. Streams and processes the uploaded video file.
    3. Persists extracted numerical features and evidence-based screening interpretation.
    4. Deterministically releases all temporary resources.
    """
    patient_id = _get_patient_id(current_user)
    session_resp = EyeAnalysisService.create_session(db, patient_id)
    temp_path = _save_upload_to_temp(file)
    try:
        return EyeAnalysisService.process_video(
            db=db,
            patient_id=patient_id,
            session_id=session_resp.id,
            video_path=temp_path,
            max_frames=max_frames,
            max_duration_sec=max_duration_sec
        )
    finally:
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass


@router.post(
    "/sample-video-screening",
    response_model=EyeAnalysisSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate and process synthetic sample video (normal, horizontal_nystagmus, vertical_nystagmus)"
)
def create_sample_video_screening(
    pattern: str = Query("normal", description="Movement pattern: 'normal', 'horizontal_nystagmus', 'vertical_nystagmus'"),
    current_user: User = Depends(require_patient),
    db: Session = Depends(get_db)
):
    """
    Convenience screening endpoint for testing and verification:
    Generates a 3-second synthetic eye video matching the requested kinematic pattern,
    processes it through the real OpenCV CVPipeline, and returns the calibrated screening interpretation.
    """
    if pattern not in ("normal", "horizontal_nystagmus", "vertical_nystagmus"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pattern must be one of: 'normal', 'horizontal_nystagmus', 'vertical_nystagmus'"
        )
    patient_id = _get_patient_id(current_user)
    return EyeAnalysisService.process_sample_video(db=db, patient_id=patient_id, pattern=pattern)


