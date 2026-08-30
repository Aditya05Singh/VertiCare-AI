import math
from typing import Dict, Tuple, Optional, Any
from cv.src.schemas import NormalizedEyePosition


def euclidean_distance(p1: Tuple[float, float, ...], p2: Tuple[float, float, ...]) -> float:
    """Compute 2D euclidean distance between two normalized coordinate points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def calculate_eye_aspect_ratio(eye_pts: Dict[str, Tuple[float, float, float]]) -> float:
    """
    Calculate Eye Aspect Ratio (EAR) using standard 6-point ocular landmark topology.
    EAR = (|top - bottom| + |top_alt - bottom_alt|) / (2 * |outer - inner|)
    """
    try:
        top = eye_pts.get("top", (0.0, 0.0, 0.0))
        bottom = eye_pts.get("bottom", (0.0, 0.0, 0.0))
        top_alt = eye_pts.get("top_alt", top)
        bottom_alt = eye_pts.get("bottom_alt", bottom)
        outer = eye_pts.get("outer", (0.0, 0.0, 0.0))
        inner = eye_pts.get("inner", (0.0, 0.0, 0.0))

        v1 = euclidean_distance(top, bottom)
        v2 = euclidean_distance(top_alt, bottom_alt)
        h = euclidean_distance(outer, inner)

        if h <= 1e-6:
            return 0.0

        ear = (v1 + v2) / (2.0 * h)
        return float(ear)
    except Exception:
        return 0.0


def extract_normalized_eye_position(raw_landmarks: Dict[str, Any]) -> Optional[NormalizedEyePosition]:
    """
    Normalize ocular positions relative to facial scale (inter-ocular distance).
    Normalizes coordinates so head distance and resolution do not distort feature extraction.
    """
    if not raw_landmarks or not raw_landmarks.get("face_detected"):
        return None

    left_pts = raw_landmarks.get("left_eye", {})
    right_pts = raw_landmarks.get("right_eye", {})

    if not left_pts or not right_pts:
        return None

    # Compute inter-ocular distance between outer corners as scaling baseline
    left_outer = left_pts.get("outer", (0.0, 0.0, 0.0))
    right_outer = right_pts.get("outer", (0.0, 0.0, 0.0))
    iod = euclidean_distance(left_outer, right_outer)

    if iod <= 1e-6:
        iod = 1.0  # Prevent zero division

    # Midpoint between outer corners as coordinate origin
    mid_x = (left_outer[0] + right_outer[0]) / 2.0
    mid_y = (left_outer[1] + right_outer[1]) / 2.0

    # Determine left and right pupil/iris centers (or inner centroid)
    left_iris = left_pts.get("iris_center")
    if not left_iris or left_iris[0] == 0.0:
        left_inner = left_pts.get("inner", left_outer)
        left_center = ((left_outer[0] + left_inner[0]) / 2.0, (left_outer[1] + left_inner[1]) / 2.0)
    else:
        left_center = (left_iris[0], left_iris[1])

    right_iris = right_pts.get("iris_center")
    if not right_iris or right_iris[0] == 0.0:
        right_inner = right_pts.get("inner", right_outer)
        right_center = ((right_outer[0] + right_inner[0]) / 2.0, (right_outer[1] + right_inner[1]) / 2.0)
    else:
        right_center = (right_iris[0], right_iris[1])

    # Scale-normalized displacement coordinates
    norm_left_x = (left_center[0] - mid_x) / iod
    norm_left_y = (left_center[1] - mid_y) / iod
    norm_right_x = (right_center[0] - mid_x) / iod
    norm_right_y = (right_center[1] - mid_y) / iod

    left_ear = calculate_eye_aspect_ratio(left_pts)
    right_ear = calculate_eye_aspect_ratio(right_pts)

    return NormalizedEyePosition(
        left_x=float(norm_left_x),
        left_y=float(norm_left_y),
        right_x=float(norm_right_x),
        right_y=float(norm_right_y),
        left_ear=left_ear,
        right_ear=right_ear,
        inter_ocular_distance=float(iod),
    )

