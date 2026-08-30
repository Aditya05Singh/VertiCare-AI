import pytest
from cv.src.eye_features import extract_normalized_eye_position, calculate_eye_aspect_ratio, euclidean_distance


def test_euclidean_distance():
    p1 = (0.0, 0.0)
    p2 = (3.0, 4.0)
    assert euclidean_distance(p1, p2) == 5.0


def test_calculate_eye_aspect_ratio():
    # Construct open eye geometry: height ~0.04, width ~0.10 -> EAR ~ 0.40
    open_eye = {
        "outer": (0.30, 0.50, 0.0),
        "inner": (0.40, 0.50, 0.0),
        "top": (0.35, 0.46, 0.0),
        "bottom": (0.35, 0.54, 0.0),
        "top_alt": (0.35, 0.46, 0.0),
        "bottom_alt": (0.35, 0.54, 0.0),
    }
    ear_open = calculate_eye_aspect_ratio(open_eye)
    assert ear_open > 0.30

    # Construct closed eye geometry: height ~0.005 -> EAR ~ 0.05
    closed_eye = {
        "outer": (0.30, 0.50, 0.0),
        "inner": (0.40, 0.50, 0.0),
        "top": (0.35, 0.495, 0.0),
        "bottom": (0.35, 0.505, 0.0),
        "top_alt": (0.35, 0.495, 0.0),
        "bottom_alt": (0.35, 0.505, 0.0),
    }
    ear_closed = calculate_eye_aspect_ratio(closed_eye)
    assert ear_closed < 0.15


def test_extract_normalized_eye_position_valid():
    synthetic_landmarks = {
        "face_detected": True,
        "left_eye": {
            "outer": (0.30, 0.50, 0.0),
            "inner": (0.40, 0.50, 0.0),
            "top": (0.35, 0.47, 0.0),
            "bottom": (0.35, 0.53, 0.0),
            "iris_center": (0.35, 0.50, 0.0)
        },
        "right_eye": {
            "outer": (0.70, 0.50, 0.0),
            "inner": (0.60, 0.50, 0.0),
            "top": (0.65, 0.47, 0.0),
            "bottom": (0.65, 0.53, 0.0),
            "iris_center": (0.65, 0.50, 0.0)
        },
        "image_width": 640,
        "image_height": 480
    }

    norm_pos = extract_normalized_eye_position(synthetic_landmarks)
    assert norm_pos is not None
    assert pytest.approx(norm_pos.inter_ocular_distance, 1e-4) == 0.40
    assert norm_pos.left_x < 0.0  # Left of midpoint
    assert norm_pos.right_x > 0.0  # Right of midpoint


def test_extract_normalized_eye_position_no_face():
    assert extract_normalized_eye_position(None) is None
    assert extract_normalized_eye_position({"face_detected": False}) is None
