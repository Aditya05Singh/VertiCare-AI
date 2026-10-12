"""
cv/src/pupil_ransac.py

Robust Pupil Tracking and Algebraic Ellipse Fitting with RANSAC Outlier Rejection.
Algorithm adapted and completed from reference repository:
    https://github.com/nphilip1098/pupiltrack-nystagmus (by nphilip1098)

This module provides:
1. Direct least-squares algebraic ellipse fitting.
2. RANSAC-based outlier rejection for robust ellipse fitting during eye blinks and eyelid occlusion.
3. Pupil segmentation and tracking within eye Region of Interest (ROI) images.
"""

from typing import Optional, Tuple, Dict, Any, List
import numpy as np
import cv2


def fit_rotated_ellipse(data: np.ndarray) -> Optional[Tuple[float, float, float, float, float]]:
    """
    Fit a general rotated conic section (ellipse) using direct algebraic least squares:
        x^2 + b*x*y + c*y^2 + d*x + e*y + f = 0
    with a = 1.0 normalization.

    Returns:
        (cx, cy, a_axis, b_axis, theta) in pixels/radians, or None if the fit is degenerate.
    """
    if data is None or len(data) < 5:
        return None

    mean_x = float(np.mean(data[:, 0]))
    mean_y = float(np.mean(data[:, 1]))

    xs = (data[:, 0].astype(np.float64) - mean_x).reshape(-1, 1)
    ys = (data[:, 1].astype(np.float64) - mean_y).reshape(-1, 1)

    # Design matrix J: [x*y, y^2, x, y, 1]
    J = np.hstack((xs * ys, ys ** 2, xs, ys, np.ones_like(xs, dtype=np.float64)))
    Y = -1.0 * (xs ** 2)

    try:
        # Solve least squares: J * P = Y  =>  P = (J^T * J)^(-1) * J^T * Y
        JT = J.T
        JT_J = np.dot(JT, J)
        if np.linalg.cond(JT_J) > 1e12:
            return None  # Ill-conditioned
        inv_JT_J = np.linalg.inv(JT_J)
        P = np.dot(inv_JT_J, np.dot(JT, Y))
    except (np.linalg.LinAlgError, ValueError):
        return None

    # Ellipse parameters: a*x^2 + b*x*y + c*y^2 + d*x + e*y + f = 0
    a = 1.0
    b = float(P[0, 0])
    c = float(P[1, 0])
    d = float(P[2, 0])
    e = float(P[3, 0])
    f = float(P[4, 0])

    denom = b ** 2 - 4.0 * a * c
    # For an ellipse, discriminant b^2 - 4ac must be negative
    if denom >= 0:
        return None

    # Center coordinates in original reference frame
    cx = float((2.0 * c * d - b * e) / denom) + mean_x
    cy = float((2.0 * a * e - b * d) / denom) + mean_y

    # Orientation angle
    if np.abs(b) < 1e-7 and np.abs(a - c) < 1e-7:
        theta = 0.0
    else:
        theta = 0.5 * float(np.arctan2(b, (a - c)))

    # Semi-axes length calculation
    term = np.sqrt((a - c) ** 2 + b ** 2)
    numerator = 2.0 * (a * e ** 2 + c * d ** 2 - b * d * e + denom * f)

    denom_axis_a = denom * ((a + c) + term)
    denom_axis_b = denom * ((a + c) - term)

    if np.abs(denom_axis_a) < 1e-12 or np.abs(denom_axis_b) < 1e-12:
        return None

    val_a = -numerator / denom_axis_a
    val_b = -numerator / denom_axis_b

    if val_a <= 0 or val_b <= 0:
        return None

    a_axis = float(np.sqrt(val_a))
    b_axis = float(np.sqrt(val_b))

    # Sanity checks on axes dimensions
    if not (np.isfinite(cx) and np.isfinite(cy) and np.isfinite(a_axis) and np.isfinite(b_axis)):
        return None
    if a_axis <= 0 or b_axis <= 0 or a_axis > 5000 or b_axis > 5000:
        return None

    return (cx, cy, a_axis, b_axis, theta)


def fit_rotated_ellipse_ransac(
    data: np.ndarray,
    n_iter: int = 50,
    sample_num: int = 10,
    offset: float = 80.0,
    min_inliers: int = 8,
    random_state: Optional[int] = None
) -> Optional[Tuple[float, float, float, float, float]]:
    """
    RANSAC-based algebraic ellipse fitting for robust outlier rejection during blink artifacts.
    Iteratively samples random subsets of contour points, fits algebraic ellipse, and selects
    the candidate with the maximum inlier count within algebraic distance `offset`.

    Parameters:
        data: Array of (x, y) contour points (N x 2).
        n_iter: Number of RANSAC iterations.
        sample_num: Number of points sampled per iteration (>= 5).
        offset: Algebraic residual tolerance threshold.
        min_inliers: Minimum inliers required to accept fit.
        random_state: Optional random seed for reproducible tests.
    """
    if data is None or len(data) < sample_num or sample_num < 5:
        return None

    rng = np.random.default_rng(random_state)
    best_inlier_count = 0
    best_inlier_sample: Optional[np.ndarray] = None

    n_points = len(data)

    for _ in range(n_iter):
        indices = rng.choice(n_points, size=sample_num, replace=False)
        candidate_pts = data[indices]

        # Fit candidate model
        try:
            fit = fit_rotated_ellipse(candidate_pts)
            if fit is None:
                continue

            cx, cy, a_axis, b_axis, theta = fit
            # Check algebraic residual for all points
            xs = data[:, 0]
            ys = data[:, 1]
            # Conic coefficients
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)
            x_rot = (xs - cx) * cos_t + (ys - cy) * sin_t
            y_rot = -(xs - cx) * sin_t + (ys - cy) * cos_t
            geometric_dist = (x_rot / max(a_axis, 1e-4)) ** 2 + (y_rot / max(b_axis, 1e-4)) ** 2

            # Inliers: normalized geometric distance close to 1.0
            inliers = data[np.abs(geometric_dist - 1.0) < (offset / 100.0)]
            inlier_count = len(inliers)

            if inlier_count > best_inlier_count:
                best_inlier_count = inlier_count
                best_inlier_sample = inliers
        except Exception:
            continue

    if best_inlier_count >= min_inliers and best_inlier_sample is not None and len(best_inlier_sample) >= 5:
        # Refit on all inliers
        final_fit = fit_rotated_ellipse(best_inlier_sample)
        if final_fit is not None:
            return final_fit

    # Fallback to direct fit if RANSAC did not find enough consensus
    if len(data) >= 5:
        return fit_rotated_ellipse(data)
    return None


def detect_pupil_in_eye_roi(
    eye_image: np.ndarray,
    use_ransac: bool = True,
    dark_threshold_ratio: float = 0.25
) -> Optional[Dict[str, Any]]:
    """
    Segment and track pupil within a close-up eye region of interest (ROI) image.
    Uses adaptive/intensity thresholding, contour extraction, and RANSAC ellipse fitting.

    Parameters:
        eye_image: BGR or Grayscale eye crop image.
        use_ransac: Whether to use RANSAC outlier rejection.
        dark_threshold_ratio: Intensity quantile for pupil dark threshold.

    Returns:
        Dictionary with pupil center (cx, cy), semi-axes, angle, and detection status,
        or None if no pupil candidate detected.
    """
    if eye_image is None or not isinstance(eye_image, np.ndarray) or eye_image.size == 0:
        return None

    if len(eye_image.shape) == 3:
        gray = cv2.cvtColor(eye_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = eye_image.copy()

    h, w = gray.shape[:2]
    if h < 10 or w < 10:
        return None

    # 1. Contrast enhancement and noise smoothing
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 2. Adaptive thresholding targeting dark pupil disk
    min_val, max_val, _, _ = cv2.minMaxLoc(blurred)
    thresh_val = min_val + (max_val - min_val) * dark_threshold_ratio
    _, binary = cv2.threshold(blurred, int(thresh_val), 255, cv2.THRESH_BINARY_INV)

    # 3. Morphological opening to detach eyelashes/eyelids
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    # 4. Find external contours
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None

    # Filter contours by minimum area (pupil must have reasonable size in ROI)
    min_area = (h * w) * 0.005
    max_area = (h * w) * 0.70
    valid_contours = [c for c in contours if min_area < cv2.contourArea(c) < max_area]
    if not valid_contours:
        return None

    # Select largest circular/elliptical dark contour
    best_contour = max(valid_contours, key=cv2.contourArea)
    pts = best_contour.reshape(-1, 2)

    if len(pts) < 5:
        # Fallback to center of mass
        M = cv2.moments(best_contour)
        if M["m00"] > 0:
            cx = float(M["m10"] / M["m00"])
            cy = float(M["m01"] / M["m00"])
            return {
                "cx": cx,
                "cy": cy,
                "a_axis": float(np.sqrt(M["m00"] / np.pi)),
                "b_axis": float(np.sqrt(M["m00"] / np.pi)),
                "theta": 0.0,
                "confidence": 0.5,
                "method": "moments_fallback"
            }
        return None

    # 5. Fit ellipse using RANSAC or direct fit
    if use_ransac and len(pts) >= 10:
        fit = fit_rotated_ellipse_ransac(pts, n_iter=40, sample_num=8, offset=50.0)
        method = "ransac_ellipse"
    else:
        fit = fit_rotated_ellipse(pts)
        method = "direct_ellipse"

    if fit is None:
        # Fallback to OpenCV cv2.fitEllipse if points >= 5
        try:
            if len(pts) >= 5:
                (ocx, ocy), (d1, d2), oangle = cv2.fitEllipse(best_contour)
                return {
                    "cx": float(ocx),
                    "cy": float(ocy),
                    "a_axis": float(d1 / 2.0),
                    "b_axis": float(d2 / 2.0),
                    "theta": float(np.radians(oangle)),
                    "confidence": 0.65,
                    "method": "opencv_fit_ellipse"
                }
        except Exception:
            pass
        return None

    cx, cy, a_axis, b_axis, theta = fit
    # Quality score based on axis ratio and ROI bounds
    axis_ratio = min(a_axis, b_axis) / max(a_axis, b_axis, 1e-4)
    in_bounds = (0 <= cx <= w) and (0 <= cy <= h)
    confidence = float(axis_ratio * 0.9 if in_bounds else 0.3)

    return {
        "cx": round(cx, 3),
        "cy": round(cy, 3),
        "a_axis": round(a_axis, 3),
        "b_axis": round(b_axis, 3),
        "theta": round(theta, 4),
        "confidence": round(confidence, 3),
        "method": method
    }
