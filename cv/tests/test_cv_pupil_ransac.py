"""
cv/tests/test_cv_pupil_ransac.py

Unit and integration tests for RANSAC algebraic ellipse fitting,
pupil detection in eye ROI, and real benchmark 1D pupil trajectory analysis.
"""

from pathlib import Path
import pytest
import numpy as np

from cv.src.pupil_ransac import (
    fit_rotated_ellipse,
    fit_rotated_ellipse_ransac,
    detect_pupil_in_eye_roi,
)
from cv.src.movement_analysis import analyze_1d_trajectory
from cv.src.capture import SyntheticFrameGenerator


def test_fit_rotated_ellipse_perfect_points():
    """Verify algebraic ellipse fit on known geometric ellipse points."""
    cx_true, cy_true = 50.0, 60.0
    a_true, b_true = 20.0, 10.0
    theta_true = 0.3  # radians

    angles = np.linspace(0, 2 * np.pi, 30, endpoint=False)
    x = a_true * np.cos(angles)
    y = b_true * np.sin(angles)

    cos_t, sin_t = np.cos(theta_true), np.sin(theta_true)
    xr = cx_true + x * cos_t - y * sin_t
    yr = cy_true + x * sin_t + y * cos_t
    pts = np.column_stack((xr, yr))

    fit = fit_rotated_ellipse(pts)
    assert fit is not None
    cx, cy, a_axis, b_axis, theta = fit
    assert np.isclose(cx, cx_true, atol=0.5)
    assert np.isclose(cy, cy_true, atol=0.5)
    assert np.isclose(min(a_axis, b_axis), min(a_true, b_true), atol=1.0)
    assert np.isclose(max(a_axis, b_axis), max(a_true, b_true), atol=1.0)


def test_fit_rotated_ellipse_ransac_with_outliers():
    """Verify RANSAC successfully rejects outliers from extreme blink artifacts."""
    cx_true, cy_true = 100.0, 100.0
    a_true, b_true = 25.0, 15.0

    angles = np.linspace(0, 2 * np.pi, 25, endpoint=False)
    x = cx_true + a_true * np.cos(angles)
    y = cy_true + b_true * np.sin(angles)
    inliers = np.column_stack((x, y))

    # Add 10 extreme outliers mimicking eyelashes / blink occlusion
    rng = np.random.default_rng(42)
    outliers = rng.uniform(20.0, 200.0, size=(10, 2))
    noisy_pts = np.vstack([inliers, outliers])

    fit = fit_rotated_ellipse_ransac(noisy_pts, n_iter=60, sample_num=8, offset=30.0, random_state=42)
    assert fit is not None
    cx, cy, a_axis, b_axis, _ = fit
    assert np.isclose(cx, cx_true, atol=3.0)
    assert np.isclose(cy, cy_true, atol=3.0)


def test_fit_rotated_ellipse_degenerate_collinear():
    """Verify degenerate collinear points return None without crashing."""
    collinear_pts = np.array([[i, i] for i in range(15)], dtype=np.float64)
    fit = fit_rotated_ellipse(collinear_pts)
    assert fit is None


def test_detect_pupil_in_eye_roi():
    """Verify pupil segmentation and center tracking on synthetic rendered eye ROI."""
    roi = SyntheticFrameGenerator.render_synthetic_eye_frame(
        width=200, height=150, pupil_x_norm=0.5, pupil_y_norm=0.5, pupil_radius=12
    )
    result = detect_pupil_in_eye_roi(roi, use_ransac=True)
    assert result is not None
    assert "cx" in result
    assert "cy" in result
    assert 0 <= result["cx"] <= 200
    assert 0 <= result["cy"] <= 150
    assert result["confidence"] > 0.3


def test_detect_pupil_in_empty_or_blank_roi():
    """Verify blank ROI produces None gracefully."""
    blank = np.zeros((100, 100, 3), dtype=np.uint8)
    res = detect_pupil_in_eye_roi(blank)
    assert res is None


def test_analyze_real_pupil_xcords_dataset():
    """
    Genuine end-to-end analysis on real benchmark dataset:
    cv/data/pupil_xcords.csv (2,770 pupil horizontal coordinates from pupiltrack-nystagmus).
    """
    csv_path = Path(__file__).resolve().parent.parent / "data" / "pupil_xcords.csv"
    assert csv_path.exists(), f"Benchmark dataset missing at {csv_path}"

    with open(csv_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    coords = np.array([float(val) for val in lines], dtype=np.float64)
    assert len(coords) == 2769

    # Analyze 1D trajectory (nominal 30 fps)
    analysis = analyze_1d_trajectory(coords, dt=1.0 / 30.0, axis_name="horizontal")

    assert analysis["status"] == "ANALYZED"
    assert analysis["sample_count"] == 2769
    assert analysis["amplitude"] > 0.0
    assert analysis["velocity_mean"] > 0.0
    assert analysis["dominant_frequency_hz"] >= 0.0
    assert "Does not establish medical diagnosis" in analysis["clinical_disclaimer"]
