from typing import List, Optional, Dict, Any
import numpy as np
from cv.src.landmarks import MediaPipeLandmarkAdapter
from cv.src.eye_features import extract_normalized_eye_position
from cv.src.movement_analysis import calculate_quality_summary, extract_movement_features
from cv.src.capture import normalize_frame_format
from cv.src.schemas import (
    TemporalSample,
    QualitySummary,
    MovementFeatures,
    CVAnalysisResult,
    NormalizedEyePosition
)


class CVPipeline:
    """
    Modular Computer-Vision Eye-Movement Screening Pipeline.
    Processes video frames or temporal sample sequences into verified numerical features and technical quality metrics.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id
        self.detector = MediaPipeLandmarkAdapter()
        self.samples: List[TemporalSample] = []
        self.total_frames_received: int = 0

    def reset(self) -> None:
        """Clear temporal buffers."""
        self.samples.clear()
        self.total_frames_received = 0

    def add_sample(self, sample: TemporalSample) -> None:
        """Directly append a temporal eye-tracking sample (useful for hardware-independent unit testing)."""
        self.total_frames_received += 1
        self.samples.append(sample)

    def process_frame(self, frame: np.ndarray, timestamp: float) -> Optional[NormalizedEyePosition]:
        """
        Process a single image frame:
        1. Normalizes image format (RGB, 640x480).
        2. Detects facial/ocular landmarks.
        3. Normalizes 2D coordinates relative to inter-ocular scale.
        4. Records timestamped sample into temporal buffer.
        """
        self.total_frames_received += 1

        norm_frame = normalize_frame_format(frame)
        if norm_frame is None:
            self.samples.append(TemporalSample(timestamp=timestamp, left_x=0.0, left_y=0.0, right_x=0.0, right_y=0.0, valid=False))
            return None

        raw_landmarks = self.detector.extract_landmarks(norm_frame)
        if raw_landmarks is None or not raw_landmarks.get("face_detected"):
            self.samples.append(TemporalSample(timestamp=timestamp, left_x=0.0, left_y=0.0, right_x=0.0, right_y=0.0, valid=False))
            return None

        norm_eye_pos = extract_normalized_eye_position(raw_landmarks)
        if norm_eye_pos is None:
            self.samples.append(TemporalSample(timestamp=timestamp, left_x=0.0, left_y=0.0, right_x=0.0, right_y=0.0, valid=False))
            return None

        self.samples.append(
            TemporalSample(
                timestamp=timestamp,
                left_x=norm_eye_pos.left_x,
                left_y=norm_eye_pos.left_y,
                right_x=norm_eye_pos.right_x,
                right_y=norm_eye_pos.right_y,
                left_ear=norm_eye_pos.left_ear,
                right_ear=norm_eye_pos.right_ear,
                valid=True
            )
        )
        return norm_eye_pos

    def analyze(self) -> CVAnalysisResult:
        """
        Extract longitudinal movement features, compute technical quality score,
        and generate a non-diagnostic CV result packet.
        """
        quality = calculate_quality_summary(self.samples, self.total_frames_received)

        if not quality.is_sufficient:
            features = extract_movement_features(self.samples)
            return CVAnalysisResult(
                session_id=self.session_id,
                status="INSUFFICIENT_QUALITY",
                quality=quality,
                features=features,
                observation={
                    "status": "INSUFFICIENT_QUALITY",
                    "message": "Tracking quality fell below technical threshold. Please record in adequate lighting facing the camera directly."
                }
            )

        features = extract_movement_features(self.samples)
        return CVAnalysisResult(
            session_id=self.session_id,
            status="COMPLETED",
            quality=quality,
            features=features,
            observation={
                "status": "FEATURES_AVAILABLE",
                "message": "Computer-vision eye-movement features extracted successfully."
            }
        )

