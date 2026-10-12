"""
cv/src/pipeline.py

Modular Computer-Vision Eye-Movement Screening and Video Analysis Pipeline.
Processes video files, frame streams, or temporal sample sequences into verified
numerical features, technical quality metrics, and parameterized oscillation observations.
"""

from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import numpy as np
import cv2

from cv.src.landmarks import MediaPipeLandmarkAdapter
from cv.src.pupil_ransac import detect_pupil_in_eye_roi
from cv.src.eye_features import extract_normalized_eye_position
from cv.src.movement_analysis import (
    calculate_quality_summary,
    extract_movement_features,
    analyze_nystagmus_kinematics
)
from cv.src.capture import normalize_frame_format, VideoFileProcessor, VideoProcessingError
from cv.src.schemas import (
    TemporalSample,
    QualitySummary,
    MovementFeatures,
    CVAnalysisResult,
    NormalizedEyePosition,
    VideoMetadata
)


class CVPipeline:
    """
    Modular Computer-Vision Eye-Movement Screening Pipeline.
    Supports:
    - Live webcam frame streams (via MediaPipe iris landmarks or direct pupil detection).
    - Video files (.mp4, .avi, .mov, .webm) with automated validation and resource cleanup.
    - Close-up eye/VOG feeds using RANSAC ellipse pupil tracking.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id
        self.detector = MediaPipeLandmarkAdapter()
        self.samples: List[TemporalSample] = []
        self.total_frames_received: int = 0
        self.video_metadata: Optional[VideoMetadata] = None

    def reset(self) -> None:
        """Clear temporal buffers and reset frame counters."""
        self.samples.clear()
        self.total_frames_received = 0
        self.video_metadata = None

    def add_sample(self, sample: TemporalSample) -> None:
        """Directly append a temporal eye-tracking sample (useful for hardware-independent unit testing)."""
        self.total_frames_received += 1
        self.samples.append(sample)

    def process_frame(self, frame: np.ndarray, timestamp: float) -> Optional[NormalizedEyePosition]:
        """
        Process a single image frame:
        1. Validates and normalizes format.
        2. Tries MediaPipe facial/ocular mesh detector.
        3. Falls back to direct close-up RANSAC pupil detection if full face is not detected.
        4. Records timestamped sample into temporal buffer.
        """
        self.total_frames_received += 1

        norm_frame = normalize_frame_format(frame)
        if norm_frame is None:
            self.samples.append(TemporalSample(timestamp=timestamp, left_x=0.0, left_y=0.0, right_x=0.0, right_y=0.0, valid=False))
            return None

        # 1. Try MediaPipe full-face landmarker
        raw_landmarks = self.detector.extract_landmarks(norm_frame)
        if raw_landmarks is not None and raw_landmarks.get("face_detected"):
            norm_eye_pos = extract_normalized_eye_position(raw_landmarks)
            if norm_eye_pos is not None:
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

        # 2. Secondary / Direct close-up eye tracking (RANSAC pupil fit)
        # Useful for zoomed-in ocular/VOG feeds where full face is not present
        pupil_fit = detect_pupil_in_eye_roi(frame, use_ransac=True)
        if pupil_fit is not None and pupil_fit.get("confidence", 0.0) >= 0.4:
            h, w = frame.shape[:2]
            norm_x = float(pupil_fit["cx"] / max(w, 1))
            norm_y = float(pupil_fit["cy"] / max(h, 1))
            self.samples.append(
                TemporalSample(
                    timestamp=timestamp,
                    left_x=norm_x - 0.1,
                    left_y=norm_y,
                    right_x=norm_x + 0.1,
                    right_y=norm_y,
                    left_ear=0.28,
                    right_ear=0.28,
                    valid=True
                )
            )
            return NormalizedEyePosition(left_x=norm_x - 0.1, left_y=norm_y, right_x=norm_x + 0.1, right_y=norm_y)

        # Frame invalid / no eyes detected
        self.samples.append(TemporalSample(timestamp=timestamp, left_x=0.0, left_y=0.0, right_x=0.0, right_y=0.0, valid=False))
        return None

    def process_video_file(
        self,
        video_path: Union[str, Path],
        max_frames: int = 1800,
        max_duration_sec: float = 60.0
    ) -> CVAnalysisResult:
        """
        End-to-end video file processor:
        - Validates video container and extracts technical metadata.
        - Sequentially reads frames and extracts ocular trajectories.
        - Executes parameterized oscillation analysis and returns structured CVAnalysisResult.
        Guarantees complete file handle and memory cleanup.
        """
        self.reset()
        v_path = Path(video_path)

        try:
            self.video_metadata = VideoFileProcessor.inspect_and_validate(v_path)
        except Exception as e:
            return CVAnalysisResult(
                session_id=self.session_id,
                status="FAILED",
                quality=QualitySummary(0, 0, 0.0, 0.0, False),
                features=MovementFeatures(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0.0),
                observation={"status": "ERROR", "message": f"Video validation failed: {str(e)}"},
                warnings=[str(e)],
                limitations=["Input video could not be read or processed."]
            )

        # Extract frames with strict limits and guaranteed resource cleanup
        try:
            for frame_idx, timestamp, frame in VideoFileProcessor.extract_frames(
                v_path, max_frames=max_frames, max_duration_sec=max_duration_sec
            ):
                self.process_frame(frame, timestamp)
        except Exception as e:
            result = self.analyze()
            result.status = "PARTIAL_ERROR"
            result.warnings.append(f"Frame processing error: {str(e)}")
            return result

        result = self.analyze()
        result.video_metadata = self.video_metadata
        return result

    def analyze(self) -> CVAnalysisResult:
        """
        Extract longitudinal movement features, compute technical quality score,
        execute parameterized oscillation analysis, and generate a non-diagnostic CV result packet.
        """
        quality = calculate_quality_summary(self.samples, self.total_frames_received)
        features = extract_movement_features(self.samples)
        warnings: List[str] = []
        limitations: List[str] = [
            "Observational computer-vision feature extraction only.",
            "Pupil tracking and ocular movement parameters do not constitute a medical diagnosis.",
            "Visual artifacts, head motion, or poor lighting can introduce noise into kinematic measures."
        ]

        if not quality.is_sufficient:
            warnings.append(
                f"Valid frame ratio ({quality.valid_ratio:.2f}) or sample count ({quality.valid_frames}) below threshold."
            )
            return CVAnalysisResult(
                session_id=self.session_id,
                status="INSUFFICIENT_QUALITY",
                quality=quality,
                features=features,
                video_metadata=self.video_metadata,
                observation={
                    "status": "INSUFFICIENT_QUALITY",
                    "message": "Tracking quality fell below technical threshold. Please record in adequate lighting facing the camera directly."
                },
                nystagmus_analysis=None,
                warnings=warnings,
                limitations=limitations
            )

        # Execute parameterized nystagmus kinematic analysis
        nystagmus_res = analyze_nystagmus_kinematics(self.samples)

        return CVAnalysisResult(
            session_id=self.session_id,
            status="COMPLETED",
            quality=quality,
            features=features,
            video_metadata=self.video_metadata,
            observation={
                "status": "FEATURES_AVAILABLE",
                "message": "Computer-vision eye-movement features and oscillatory kinematics extracted successfully.",
                "dominant_axis": nystagmus_res.get("dominant_axis", "INDETERMINATE"),
                "pattern_type": nystagmus_res.get("pattern_type", "INDETERMINATE")
            },
            nystagmus_analysis=nystagmus_res,
            warnings=warnings,
            limitations=limitations
        )
