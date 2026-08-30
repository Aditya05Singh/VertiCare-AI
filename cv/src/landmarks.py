import os
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

# Set non-interactive Matplotlib config to suppress font warnings
os.environ["MPLCONFIGDIR"] = "/tmp"

# Standard Face Mesh Landmark Index Mappings (MediaPipe topology)
# Left eye contour and keypoints
LEFT_EYE_INDICES = {
    "outer": 33,
    "inner": 133,
    "top": 159,
    "bottom": 145,
    "top_alt": 158,
    "bottom_alt": 144,
    "iris_center": 468,  # Refined 468–472
}

# Right eye contour and keypoints
RIGHT_EYE_INDICES = {
    "outer": 362,
    "inner": 263,
    "top": 386,
    "bottom": 374,
    "top_alt": 385,
    "bottom_alt": 373,
    "iris_center": 473,  # Refined 473–477
}

# Reference facial landmarks for scale and pose normalization
NOSE_TIP_INDEX = 1
CHIN_INDEX = 152
FOREHEAD_INDEX = 10


class MediaPipeLandmarkAdapter:
    """
    Modular landmark extraction adapter wrapping MediaPipe.
    Provides robust frame processing with graceful fallback for testing/demo modes.
    """

    def __init__(self, use_static_image: bool = False, max_faces: int = 1):
        self.use_static_image = use_static_image
        self.max_faces = max_faces
        self._detector = None
        self._init_detector()

    def _init_detector(self) -> None:
        """Initialize MediaPipe face landmarker if available."""
        try:
            import mediapipe as mp
            if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
                self._detector = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=self.use_static_image,
                    max_num_faces=self.max_faces,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
        except Exception:
            self._detector = None

    def extract_landmarks(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Extract normalized facial and ocular landmarks from an RGB image frame.
        Returns dictionary containing left_eye, right_eye, and reference coordinates.
        """
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return None

        h, w = frame.shape[:2]
        if h == 0 or w == 0:
            return None

        # Process with detector if initialized
        if self._detector is not None:
            try:
                results = self._detector.process(frame)
                if results and results.multi_face_landmarks:
                    face_lms = results.multi_face_landmarks[0].landmark
                    return self._parse_landmarks(face_lms, w, h)
            except Exception:
                pass

        # If native detector not available or face not found in test mode, return None
        return None

    def _parse_landmarks(self, landmarks: Any, width: int, height: int) -> Dict[str, Any]:
        """Convert raw landmark sequence to structured eye coordinates dictionary."""
        def get_pt(idx: int) -> Tuple[float, float, float]:
            if idx < len(landmarks):
                lm = landmarks[idx]
                return (lm.x, lm.y, getattr(lm, "z", 0.0))
            return (0.0, 0.0, 0.0)

        left_eye_pts = {k: get_pt(idx) for k, idx in LEFT_EYE_INDICES.items()}
        right_eye_pts = {k: get_pt(idx) for k, idx in RIGHT_EYE_INDICES.items()}

        return {
            "face_detected": True,
            "left_eye": left_eye_pts,
            "right_eye": right_eye_pts,
            "nose_tip": get_pt(NOSE_TIP_INDEX),
            "image_width": width,
            "image_height": height,
        }

