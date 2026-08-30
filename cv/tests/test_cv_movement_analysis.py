import pytest
import numpy as np
from cv.src.schemas import TemporalSample
from cv.src.movement_analysis import extract_movement_features, calculate_quality_summary


def test_velocity_and_amplitude_calculation_with_known_sequence():
    """
    Test mathematically verified sequence:
    Position x: [0.10, 0.20, 0.40]
    Timestamps: [0.0, 0.1, 0.2]
    Delta x: [0.10, 0.20]
    Delta t: [0.10, 0.10]
    Velocities: [1.0, 2.0] -> mean velocity: 1.5
    Amplitude: 0.40 - 0.10 = 0.30
    """
    samples = [
        TemporalSample(timestamp=0.0, left_x=0.10, left_y=0.5, right_x=0.10, right_y=0.5, valid=True),
        TemporalSample(timestamp=0.1, left_x=0.20, left_y=0.5, right_x=0.20, right_y=0.5, valid=True),
        TemporalSample(timestamp=0.2, left_x=0.40, left_y=0.5, right_x=0.40, right_y=0.5, valid=True),
    ]

    features = extract_movement_features(samples)
    assert pytest.approx(features.horizontal_amplitude, 0.001) == 0.30
    assert pytest.approx(features.horizontal_velocity_mean, 0.001) == 1.50
    assert pytest.approx(features.horizontal_velocity_max, 0.001) == 2.00


def test_direction_changes_calculation():
    # Signal oscillating horizontally: 0.0 -> 0.10 -> 0.0 -> 0.10 -> 0.0
    # Velocities: +1.0, -1.0, +1.0, -1.0 -> 3 direction reversals
    timestamps = [0.0, 0.1, 0.2, 0.3, 0.4]
    x_positions = [0.0, 0.10, 0.0, 0.10, 0.0]

    samples = [
        TemporalSample(timestamp=t, left_x=x, left_y=0.5, right_x=x, right_y=0.5, valid=True)
        for t, x in zip(timestamps, x_positions)
    ]

    features = extract_movement_features(samples)
    assert features.direction_changes_h == 3


def test_quality_summary_calculation():
    # 8 valid samples out of 10 total frames -> valid ratio 0.80 -> sufficient
    samples = [
        TemporalSample(timestamp=i * 0.033, left_x=0.0, left_y=0.0, right_x=0.0, right_y=0.0, valid=(i < 8))
        for i in range(10)
    ]
    quality = calculate_quality_summary(samples, total_attempted_frames=10)
    assert quality.total_frames == 10
    assert quality.valid_frames == 8
    assert quality.valid_ratio == 0.80


def test_insufficient_quality_when_drop_rate_high():
    # Only 3 valid samples out of 10 total frames -> valid ratio 0.30 -> not sufficient
    samples = [
        TemporalSample(timestamp=i * 0.033, left_x=0.0, left_y=0.0, right_x=0.0, right_y=0.0, valid=(i < 3))
        for i in range(10)
    ]
    quality = calculate_quality_summary(samples, total_attempted_frames=10)
    assert quality.is_sufficient is False

