from typing import List, Tuple, Dict, Any
import numpy as np
from cv.src.schemas import TemporalSample, MovementFeatures, QualitySummary

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

