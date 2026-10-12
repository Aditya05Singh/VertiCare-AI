"""
cv/src/movement_analysis.py

Longitudinal eye movement kinematics, tracking quality assessment,
and parameterized nystagmus oscillation analysis.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from cv.src.schemas import TemporalSample, MovementFeatures, QualitySummary, NystagmusKinematicFeatures

# Minimum valid-frames ratio required for reliable CV screening
MINIMUM_VALID_FRAME_RATIO = 0.70
BLINK_EAR_THRESHOLD = 0.20
VELOCITY_NOISE_THRESHOLD = 0.01


def calculate_quality_summary(samples: List[TemporalSample], total_attempted_frames: int) -> QualitySummary:
    """Calculate technical tracking quality metrics from temporal sample sequence."""
    total = max(total_attempted_frames, len(samples))
    if total == 0:
        return QualitySummary(
            total_frames=0,
            valid_frames=0,
            valid_ratio=0.0,
            face_detected_ratio=0.0,
            is_sufficient=False
        )

    valid_count = sum(1 for s in samples if s.valid)
    valid_ratio = valid_count / total

    return QualitySummary(
        total_frames=total,
        valid_frames=valid_count,
        valid_ratio=round(valid_ratio, 4),
        face_detected_ratio=round(valid_ratio, 4),
        is_sufficient=(valid_ratio >= MINIMUM_VALID_FRAME_RATIO and valid_count >= 10)
    )


def extract_movement_features(samples: List[TemporalSample]) -> MovementFeatures:
    """
    Extract computational eye-movement features from a time-series of normalized ocular samples.
    All velocities use actual time intervals (delta_t).
    """
    valid_samples = [s for s in samples if s.valid]

    if len(valid_samples) < 2:
        return MovementFeatures(
            horizontal_amplitude=0.0,
            vertical_amplitude=0.0,
            horizontal_velocity_mean=0.0,
            vertical_velocity_mean=0.0,
            horizontal_velocity_max=0.0,
            vertical_velocity_max=0.0,
            direction_changes_h=0,
            direction_changes_v=0,
            blink_count=0,
            blink_rate_per_min=0.0,
        )

    # Average left and right eye coordinates to obtain combined gaze trajectory
    x_coords = np.array([(s.left_x + s.right_x) / 2.0 for s in valid_samples], dtype=np.float64)
    y_coords = np.array([(s.left_y + s.right_y) / 2.0 for s in valid_samples], dtype=np.float64)
    timestamps = np.array([s.timestamp for s in valid_samples], dtype=np.float64)
    ears = np.array([(s.left_ear + s.right_ear) / 2.0 for s in valid_samples], dtype=np.float64)

    # 1. Amplitude (Peak-to-Peak normalized displacement)
    h_amp = float(np.ptp(x_coords))
    v_amp = float(np.ptp(y_coords))

    # 2. Velocity computation using actual delta_t
    dt = np.diff(timestamps)
    dx = np.diff(x_coords)
    dy = np.diff(y_coords)

    # Filter out zero or negative delta_t intervals to avoid division by zero
    valid_dt_mask = dt > 1e-5
    if np.any(valid_dt_mask):
        vx = dx[valid_dt_mask] / dt[valid_dt_mask]
        vy = dy[valid_dt_mask] / dt[valid_dt_mask]

        vx_abs = np.abs(vx)
        vy_abs = np.abs(vy)

        vx_mean = float(np.mean(vx_abs))
        vy_mean = float(np.mean(vy_abs))
        vx_max = float(np.max(vx_abs))
        vy_max = float(np.max(vy_abs))

        # 3. Direction changes (sign reversals above noise floor)
        sig_vx = vx[vx_abs > VELOCITY_NOISE_THRESHOLD]
        sig_vy = vy[vy_abs > VELOCITY_NOISE_THRESHOLD]

        dir_changes_h = int(np.sum(np.diff(np.sign(sig_vx)) != 0)) if len(sig_vx) > 1 else 0
        dir_changes_v = int(np.sum(np.diff(np.sign(sig_vy)) != 0)) if len(sig_vy) > 1 else 0
    else:
        vx_mean, vy_mean, vx_max, vy_max = 0.0, 0.0, 0.0, 0.0
        dir_changes_h, dir_changes_v = 0, 0

    # 4. Blink detection (EAR dip below threshold)
    blink_count = 0
    in_blink = False
    for ear in ears:
        if ear < BLINK_EAR_THRESHOLD and not in_blink:
            blink_count += 1
            in_blink = True
        elif ear >= (BLINK_EAR_THRESHOLD + 0.04) and in_blink:
            in_blink = False

    duration_sec = float(timestamps[-1] - timestamps[0]) if len(timestamps) > 1 else 0.0
    blink_rate = (blink_count / (duration_sec / 60.0)) if duration_sec > 5.0 else float(blink_count)

    return MovementFeatures(
        horizontal_amplitude=round(h_amp, 5),
        vertical_amplitude=round(v_amp, 5),
        horizontal_velocity_mean=round(vx_mean, 5),
        vertical_velocity_mean=round(vy_mean, 5),
        horizontal_velocity_max=round(vx_max, 5),
        vertical_velocity_max=round(vy_max, 5),
        direction_changes_h=dir_changes_h,
        direction_changes_v=dir_changes_v,
        blink_count=blink_count,
        blink_rate_per_min=round(blink_rate, 2),
    )


def analyze_1d_trajectory(
    coords: np.ndarray,
    dt: float = 1.0 / 30.0,
    axis_name: str = "horizontal"
) -> Dict[str, Any]:
    """
    Parameterized oscillatory movement analysis on a 1D coordinate series
    (e.g., benchmark pupil_xcords.csv from pupiltrack-nystagmus).

    Computes:
    - Peak-to-peak oscillation amplitude
    - Dominant oscillation frequency (FFT power spectrum peak)
    - Mean and peak velocities
    - Directional reversal count
    - Slow-phase vs fast-phase velocity asymmetry ratio
    """
    clean_coords = np.asarray(coords, dtype=np.float64)
    clean_coords = clean_coords[np.isfinite(clean_coords)]

    if len(clean_coords) < 10 or dt <= 0:
        return {
            "status": "INSUFFICIENT_SAMPLES",
            "axis": axis_name,
            "sample_count": len(clean_coords),
            "dominant_frequency_hz": 0.0,
            "amplitude": 0.0,
            "velocity_mean": 0.0,
            "velocity_max": 0.0,
            "direction_changes": 0,
            "asymmetry_ratio": 1.0,
            "pattern_type": "INDETERMINATE",
            "clinical_disclaimer": "Observational feature metrics only. Does not establish medical diagnosis of nystagmus."
        }

    # 1. Amplitude
    amp = float(np.ptp(clean_coords))

    # 2. Velocity
    diffs = np.diff(clean_coords)
    velocities = diffs / dt
    abs_velocities = np.abs(velocities)

    vel_mean = float(np.mean(abs_velocities))
    vel_max = float(np.max(abs_velocities))

    # Direction changes
    sig_v = velocities[abs_velocities > VELOCITY_NOISE_THRESHOLD]
    dir_changes = int(np.sum(np.diff(np.sign(sig_v)) != 0)) if len(sig_v) > 1 else 0

    # 3. Frequency analysis via FFT
    demeaned = clean_coords - np.mean(clean_coords)
    n = len(demeaned)
    fft_vals = np.abs(np.fft.rfft(demeaned))
    fft_freqs = np.fft.rfftfreq(n, d=dt)

    # Exclude DC component (freq index 0)
    if len(fft_freqs) > 1:
        peak_idx = 1 + np.argmax(fft_vals[1:])
        dom_freq = float(fft_freqs[peak_idx])
    else:
        dom_freq = 0.0

    # 4. Slow vs Fast phase velocity asymmetry
    # Separate positive and negative slope phases
    pos_v = velocities[velocities > VELOCITY_NOISE_THRESHOLD]
    neg_v = np.abs(velocities[velocities < -VELOCITY_NOISE_THRESHOLD])

    if len(pos_v) > 0 and len(neg_v) > 0:
        mean_pos = float(np.mean(pos_v))
        mean_neg = float(np.mean(neg_v))
        ratio = max(mean_pos, mean_neg) / max(min(mean_pos, mean_neg), 1e-4)
    else:
        ratio = 1.0

    # Categorize kinematic profile
    if amp < 0.02 and vel_mean < 0.05:
        pattern = "PHYSIOLOGICAL_FIXATION"
    elif ratio > 1.8:
        pattern = "JERK_LIKE_ASYMMETRY"
    elif dom_freq > 0.5:
        pattern = "PENDULAR_LIKE_OSCILLATION"
    else:
        pattern = "IRREGULAR_DRIFT"

    return {
        "status": "ANALYZED",
        "axis": axis_name,
        "sample_count": len(clean_coords),
        "dominant_frequency_hz": round(dom_freq, 3),
        "amplitude": round(amp, 5),
        "velocity_mean": round(vel_mean, 5),
        "velocity_max": round(vel_max, 5),
        "direction_changes": dir_changes,
        "asymmetry_ratio": round(ratio, 3),
        "pattern_type": pattern,
        "clinical_disclaimer": "Observational feature metrics only. Does not establish medical diagnosis of nystagmus."
    }


def analyze_nystagmus_kinematics(samples: List[TemporalSample]) -> Dict[str, Any]:
    """
    Multidimensional nystagmus kinematic assessment comparing horizontal and vertical
    trajectories from a sequence of temporal eye tracking samples.
    """
    valid_samples = [s for s in samples if s.valid]
    if len(valid_samples) < 15:
        return {
            "status": "INSUFFICIENT_SAMPLES",
            "message": "At least 15 valid frames are required for kinematic oscillation analysis.",
            "dominant_axis": "INDETERMINATE",
            "pattern_type": "INDETERMINATE",
            "clinical_disclaimer": "Observational feature metrics only. Does not establish medical diagnosis of nystagmus."
        }

    timestamps = np.array([s.timestamp for s in valid_samples], dtype=np.float64)
    dt_arr = np.diff(timestamps)
    valid_dt = dt_arr[dt_arr > 1e-5]
    median_dt = float(np.median(valid_dt)) if len(valid_dt) > 0 else (1.0 / 30.0)

    x_coords = np.array([(s.left_x + s.right_x) / 2.0 for s in valid_samples], dtype=np.float64)
    y_coords = np.array([(s.left_y + s.right_y) / 2.0 for s in valid_samples], dtype=np.float64)

    h_analysis = analyze_1d_trajectory(x_coords, dt=median_dt, axis_name="horizontal")
    v_analysis = analyze_1d_trajectory(y_coords, dt=median_dt, axis_name="vertical")

    # Determine dominant axis of movement
    h_amp = h_analysis.get("amplitude", 0.0)
    v_amp = v_analysis.get("amplitude", 0.0)

    if h_amp > v_amp * 1.5:
        dominant_axis = "HORIZONTAL"
        primary_analysis = h_analysis
    elif v_amp > h_amp * 1.5:
        dominant_axis = "VERTICAL"
        primary_analysis = v_analysis
    else:
        dominant_axis = "MULTIAXIAL_OR_INDETERMINATE"
        primary_analysis = h_analysis

    return {
        "status": "COMPLETED",
        "dominant_axis": dominant_axis,
        "pattern_type": primary_analysis.get("pattern_type", "INDETERMINATE"),
        "dominant_frequency_hz": primary_analysis.get("dominant_frequency_hz", 0.0),
        "asymmetry_ratio": primary_analysis.get("asymmetry_ratio", 1.0),
        "horizontal": h_analysis,
        "vertical": v_analysis,
        "clinical_disclaimer": "Observational feature metrics only. Does not establish medical diagnosis of nystagmus or vestibular pathology."
    }
